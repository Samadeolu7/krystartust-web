from decimal import Decimal
from django.db import models

from client.models import Client
from django.contrib.auth.models import User
from income.models import SingletonModel

# Create your models here.

class Savings(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client.name + ' - ' + str(self.balance)

class SavingsPayment(models.Model):
    SAVINGS = 'S'
    WITHDRAWAL = 'W'
    TRANSACTION_TYPE_CHOICES = [
        (SAVINGS, 'Savings'),
        (WITHDRAWAL, 'Withdrawal'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    savings = models.ForeignKey(Savings, on_delete=models.SET_NULL, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default=f'Savings for {client.name}')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, default=SAVINGS)
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # If the record is being created 
            # Update the corresponding Savings balance
            savings_record = Savings.objects.get(client=self.client)
            if self.transaction_type == self.SAVINGS:
                savings_record.balance += Decimal(self.amount)
                self.balance = savings_record.balance
            elif self.transaction_type == self.WITHDRAWAL:
                savings_record.balance -= Decimal(self.amount)
                self.balance = savings_record.balance
            savings_record.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} - {self.get_transaction_type_display()} - {self.amount}"
    
    class Meta:
        ordering = ['payment_date', 'created_at']
    

class CompulsorySavings(SingletonModel):
    def __str__(self):
        return f'Compulsory Savings - {self.amount}'