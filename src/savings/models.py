from django.db import models

from client.models import Client
from django.contrib.auth.models import User

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
    savings = models.ForeignKey(Savings, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, default=SAVINGS)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:  # If the record is being created
            last_payment = SavingsPayment.objects.filter(client=self.client).order_by('-created_at').first()
            if last_payment:
                self.balance = last_payment.balance + self.amount
            else:
                self.balance = self.amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} - {self.get_transaction_type_display()} - {self.amount}"
    

class CompulsorySavings(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Compulsory Savings - {self.amount}'