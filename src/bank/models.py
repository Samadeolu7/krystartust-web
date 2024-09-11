from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Bank(models.Model):
    #cash in hand will be a bank
    name = models.CharField(max_length=100)
    description = models.TextField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.IntegerField()

    def __str__(self):
        return f'{self.name} - {self.balance}'
    
    class Meta:
        ordering = ['-created_at']


class BankPayment(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bank_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateField()

    def __str__(self):
        return f'{self.bank.name} - {self.amount}'
    
    def save(self, *args, **kwargs):
        self.bank_balance = self.bank.balance + self.amount
        self.bank.balance = self.bank_balance
        self.bank.save()
        super(BankPayment, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

