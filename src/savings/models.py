from decimal import Decimal
from django.db import models

from client.models import Client
from user.models import User
from income.models import SingletonModel

from django.db import models
from client.models import Client

class Savings(models.Model):
    NORMAL = 'N'
    DC = 'D'
    SAVINGS_TYPE_CHOICES = [
        (NORMAL, 'Normal Savings'),
        (DC, 'Daily Contribution')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=1, choices=SAVINGS_TYPE_CHOICES, default=NORMAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.type == self.NORMAL:
            return self.client.name + ' - ' + str(self.balance)
        else:
            return self.client.name + ' - ' + str(self.balance) + ' -DC'

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
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    savings = models.ForeignKey(Savings, on_delete=models.SET_NULL, null=True)
    bank = models.ForeignKey('bank.Bank', on_delete=models.SET_NULL, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, default=SAVINGS)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    approved = models.BooleanField(default=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            savings_record = self.savings
            if self.transaction_type == self.SAVINGS or self.transaction_type == self.DC:
                savings_record.balance += Decimal(self.amount)
                self.balance = savings_record.balance
                savings_record.save()
                super().save(*args, **kwargs)
        elif self.transaction_type == self.WITHDRAWAL:
            if self.approved:
                savings_record = self.savings
                savings_record.balance += Decimal(self.amount)
                self.balance = savings_record.balance
                savings_record.save()
                super().save(*args, **kwargs)
            if (-1*self.amount) > savings_record.balance:
                raise ValueError('Insufficient balance')
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} - {self.get_transaction_type_display()} - {self.amount}"
    
    class Meta:
        ordering = ['payment_date', 'created_at']    


class ClientContribution(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.client} - {self.amount}"


class DailyContribution(models.Model):
    client_contribution = models.ForeignKey('ClientContribution', on_delete=models.CASCADE)
    date = models.DateField()
    payment_made = models.BooleanField(default=False)
    payment = models.ForeignKey(SavingsPayment, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Toggle payment status only
        if self.pk:  # Ensure it's an existing record
            self.payment_made = not self.payment_made

        super().save(*args, **kwargs)

    def __str__(self):
        status = "Paid" if self.payment_made else "Not Paid"
        return f"{self.client_contribution.client} - {self.date} - {self.client_contribution.amount} - {status}"

    class Meta:
        unique_together = ('client_contribution', 'date')
        ordering = ['date']


class CompulsorySavings(SingletonModel):
    def __str__(self):
        return f'Compulsory Savings - {self.amount}'