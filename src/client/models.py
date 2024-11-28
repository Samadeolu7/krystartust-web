# client/models.py
from datetime import datetime
from functools import cached_property
from django.db import models, IntegrityError
from django.apps import apps
from django.db import transaction


class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('WL', 'Weekly Loan'),
        ('ML', 'Monthly Loan'),
        ('DC', 'Daily Contribution'),
    ]

    client_id = models.CharField(max_length=100, unique=True)
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

    def __str__(self):
        return f"{self.name}-{self.client_id}"  

    @cached_property
    def savings(self):
        return self.savings_set.first()

    @cached_property
    def loan(self):
        return self.loan_set.first()

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = generate_client_id(self.client_type)
        
        while True:
            try:
                with transaction.atomic():
                    super(Client, self).save(*args, **kwargs)
                break
            except IntegrityError:
                self.client_id = generate_client_id(self.client_type)

def generate_client_id(client_type):
    """Generate a unique client ID based on the client type."""
    prefix = {
        'WL': 'WL',
        'ML': 'ML',
        'DC': 'DC'
    }.get(client_type, 'CLI')

    last_client = Client.objects.filter(client_type=client_type, client_id__startswith=prefix).order_by('client_id').last()
    if not last_client:
        return f'{prefix}0001'
    
    try:
        last_id = int(last_client.client_id[len(prefix):])
    except ValueError:
        # Handle cases where the client_id does not follow the expected format
        last_id = 0
    
    new_id = last_id + 1
    return f'{prefix}{new_id:04d}'