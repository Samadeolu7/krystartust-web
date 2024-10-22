from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from bank.utils import create_bank_payment, get_cash_in_hand
from user.models import User
import uuid

# Create your models here.

class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    transportation = models.DecimalField(max_digits=10, decimal_places=2)
    food = models.DecimalField(max_digits=10, decimal_places=2)
    house_rent = models.DecimalField(max_digits=10, decimal_places=2)
    utility = models.DecimalField(max_digits=10, decimal_places=2)
    entertainment = models.DecimalField(max_digits=10, decimal_places=2)
    leave = models.DecimalField(max_digits=10, decimal_places=2)    

    def __str__(self):
        return self.user.name


class Approval(models.Model):
    Expenses = 'expenses'
    Loan = 'loan'
    Withdrawal = 'withdrawal'
    TYPES = (
        ('Expenses', Expenses),
        ('Loan', Loan),
        ('Withdrawal', Withdrawal)
    )
    type = models.CharField(max_length=100, choices=TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals', null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.comment = f"{self.user.username} requested approval for {self.type} for {self.content_object}"
            super().save(*args, **kwargs)
        else:
            if self.approved:
                if self.type == self.Withdrawal:
                    # Set the approved attribute on the related object to True
                    savings_payment = self.content_object
                    savings_payment.approved = True
                    savings = savings_payment.savings
                    savings.balance -= savings_payment.amount
                    savings_payment.balance = savings.balance
                    savings.save()
                    savings_payment.save()
                    create_bank_payment(
                        bank=savings_payment.bank,
                        description=f"Withdrawal by {savings.client.name}",
                        amount=-savings_payment.amount,
                        payment_date=savings_payment.payment_date,
                        transaction=savings_payment.transaction,
                        created_by=savings_payment.created_by
                    )
                
                self.content_object.approved = True
                self.content_object.save()
                super().save(*args, **kwargs)
            elif self.rejected:
                
                super().save(*args, **kwargs)
                # Delete the related object
                self.content_object.delete()
            else:
                super().save(*args, **kwargs)


class Transaction(models.Model):
    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', 'TRN')
        if not self.reference_number:
            self.reference_number = self.generate_reference_number(prefix)
        super().save(*args, **kwargs)

    def generate_reference_number(self, prefix='TRN'):
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        unique_part = str(uuid.uuid4())[:5].upper()
        return f"{prefix}-{unique_part}{current_month:02d}{current_year}"
