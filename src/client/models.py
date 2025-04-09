from datetime import datetime, date
from functools import cached_property
from django.db import models, IntegrityError
from django.apps import apps
from django.db import transaction
from administration.models import Tickets
from user.models import User

class Client(models.Model):
    ACTIVE = 'A'
    LAPSE = 'L'
    DORMANT = 'D'
    PROSPECT = 'P'
    ACCOUNT_STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (LAPSE, 'Lapse'),
        (DORMANT, 'Dormant'),
        (PROSPECT, 'Prospect'),
    ]
    CLIENT_TYPE_CHOICES = [
        ('WL', 'Weekly Loan'),
        ('ML', 'Monthly Loan'),
        ('DC', 'Daily Contribution'),
        ('PR', 'Prospect'),
    ]

    client_id = models.CharField(max_length=100, unique=True, db_index=True, default=None, blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    next_of_kin = models.CharField(max_length=100, null=True, blank=True)
    next_of_kin_phone = models.CharField(max_length=15, null=True, blank=True)
    group = models.ForeignKey('main.ClientGroup', on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(default=datetime.now)
    client_type = models.CharField(max_length=2, choices=CLIENT_TYPE_CHOICES, default='WL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_status = models.CharField(
        max_length=1, choices=ACCOUNT_STATUS_CHOICES, default=ACTIVE
    )

    def __str__(self):
        return f"{self.name}-{self.client_id}"

    @cached_property
    def savings(self):
        if self.group.name == 'Ajo':
            return self.savings_set.filter(type='D').first()
        return self.savings_set.first()

    @cached_property
    def loan(self):
        return self.loan_set.first()

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = generate_client_id(self.client_type)
        elif self.client_id.startswith('PR') and self.client_type != 'PR':
            self.client_id = generate_client_id(self.client_type)
            self.prospect.is_activated = True
            self.prospect.save()
        
        while True:
            try:
                with transaction.atomic():
                    super(Client, self).save(*args, **kwargs)
                break
            except IntegrityError:
                self.client_id = generate_client_id(self.client_type)

    def update_account_status(self):
        """
        Update the client's account status based on their loan activity.
        - Active: New loan after previous closed loan or less than 30 days of inactivity.
        - Lapse: Inactive for 30+ days with loan balance zero.
        - Dormant: Inactive for 60+ days.
        """
        last_payment = self.loan_set.filter(payment__isnull=False).order_by('-payment__payment_date').first()
        if not last_payment:
            new_status = Client.ACTIVE
        else:
            last_payment_date = last_payment.payment.order_by('-payment_date').first().payment_date
            days_since_last_payment = (date.today() - last_payment_date).days
    
            if days_since_last_payment >= 60:
                new_status = Client.DORMANT
                new_status_description = 'Dormant'
            elif days_since_last_payment >= 30:
                new_status = Client.LAPSE
                new_status_description = 'Lapse'
            else:
                new_status = Client.ACTIVE
                new_status_description = 'Active'
    
        if new_status != self.account_status:
            old_status = self.account_status
            old_status_description = dict(Client.ACCOUNT_STATUS_CHOICES)[old_status]

            self.account_status = new_status
            self.save(update_fields=['account_status'])
    
            if new_status in [Client.LAPSE, Client.DORMANT]:
                ticket = Tickets.objects.create(
                    client=self,
                    title=f"Account status changed to {new_status_description} for {self.name}",
                    description=(
                        f"Client {self.name} has been inactive for "
                        f"{days_since_last_payment if last_payment else 'N/A'} days. "
                        f"Status updated from {old_status_description} to {new_status_description}."
                    ),
                    priority='n',
                    closed=False,
                    created_by=User.objects.filter(is_superuser=True).first()
                )
                ticket.users.set(User.objects.all())
                ticket.save()


class Prospect(models.Model):
    LOAN_CHOICES = [
        ('WL', 'Weekly Loan'),
        ('ML', 'Monthly Loan'),
        ('BL', 'Business Loan'),
    ]
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='prospect')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loan_type = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(default=datetime.now)
    is_activated = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prospect: {self.client.name}"

def generate_client_id(client_type):
    """Generate a unique client ID based on the client type."""
    prefix = {
        'WL': 'WL',
        'ML': 'ML',
        'DC': 'DC',
        'PR': 'PR',
    }.get(client_type, 'CLI')

    last_client = Client.objects.filter(client_type=client_type, client_id__startswith=prefix).order_by('client_id').last()
    if not last_client:
        return f'{prefix}0001'
    
    try:
        last_id = int(last_client.client_id[len(prefix):])
    except ValueError:
        last_id = 0
    
    new_id = last_id + 1
    return f'{prefix}{new_id:04d}'