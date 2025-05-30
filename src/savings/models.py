from decimal import Decimal
from django.db import models
from django.urls import reverse

from administration.manager import OfficeScopedManager
from client.models import Client
from user.models import User
from income.models import SingletonModel

from django.db import models
from client.models import Client
from django.core.exceptions import ValidationError

class Savings(models.Model):
    NORMAL = 'N'
    DC = 'D'
    SAVINGS_TYPE_CHOICES = [
        (NORMAL, 'Normal Savings'),
        (DC, 'Daily Contribution')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_index=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    office = models.ForeignKey('administration.Office', on_delete=models.CASCADE, null=True, blank=True, related_name='savings')
    type = models.CharField(max_length=1, choices=SAVINGS_TYPE_CHOICES, default=NORMAL, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OfficeScopedManager()

    def __str__(self):
        if self.type == self.NORMAL:
            return str(self.client) + ' - ' + str(self.balance)
        else:
            return str(self.client) + ' - ' + str(self.balance) + ' -DC'

    # def clean(self):
    #     if self.balance < 0:
    #         raise ValidationError('Balance cannot be negative.')

    # def save(self, *args, **kwargs):
    #     self.full_clean()  # This will call the clean method
    #     super(Savings, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('client', 'type')

class SavingsPayment(models.Model):
    SAVINGS = 'S'
    WITHDRAWAL = 'W'
    DC = 'C'
    TRANSACTION_TYPE_CHOICES = [
        (SAVINGS, 'Savings'),
        (WITHDRAWAL, 'Withdrawal'),
        (DC, 'Daily Contribution')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_index=True)
    savings = models.ForeignKey(Savings, on_delete=models.SET_NULL, null=True, db_index=True)
    bank = models.ForeignKey('bank.Bank', on_delete=models.SET_NULL, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, default=SAVINGS)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='savings_payments')
    approved = models.BooleanField(default=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            savings_record = self.savings
            if self.transaction_type in [self.SAVINGS, self.DC]:
                savings_record.balance += self.amount
                self.balance = savings_record.balance
                savings_record.save(update_fields=['balance'])
            elif self.transaction_type == self.WITHDRAWAL:
                if (-1 * self.amount) > savings_record.balance:
                    raise ValueError('Insufficient balance')
                if self.approved:
                    savings_record.balance += self.amount
                    self.balance = savings_record.balance
                    savings_record.save(update_fields=['balance'])
            

            super().save(*args, **kwargs)
        else:
            if self.transaction_type == self.WITHDRAWAL and self.approved:
                savings_record = self.savings
                savings_record.balance += self.amount
                self.balance = savings_record.balance
                savings_record.save(update_fields=['balance'])
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} - {self.get_transaction_type_display()} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('savings_detail', kwargs={'client_id': self.client.pk})
    
    class Meta:
        ordering = ['payment_date', 'created_at']    


class ClientContribution(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.client} - {self.amount}"


class DailyContribution(models.Model):
    client_contribution = models.ForeignKey(ClientContribution, on_delete=models.CASCADE, related_name='daily_contributions')
    date = models.DateField()
    payment_made = models.BooleanField(default=False)
    payment = models.ForeignKey(SavingsPayment, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        status = "Paid" if self.payment_made else "Not Paid"
        return f"{self.client_contribution.client} - {self.date} - {self.client_contribution.amount} - {status}"

    class Meta:
        unique_together = ('client_contribution', 'date')
        ordering = ['date']


class CompulsorySavings(SingletonModel):
    def __str__(self):
        return f'Compulsory Savings - {self.amount}'