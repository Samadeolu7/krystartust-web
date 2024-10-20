from django.db import models

from django.contrib.auth.models import User

from main.models import Year

class Bank(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.year:
            self.year = Year.current_year() or 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.balance}'
    
    def record_payment(self, amount, description,payment_date):
        payment = BankPayment(bank=self, amount=amount,description=description, payment_date=payment_date)
        payment.save()
    class Meta:
        ordering = ['created_at']


class BankPayment(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bank_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_payments', null=True, blank=True)
    payment_date = models.DateField()

    def __str__(self):
        return f'{self.bank.name} - {self.amount}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.bank_balance = self.bank.balance
            self.bank.balance += self.amount
            self.bank.save()
        super(BankPayment, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['payment_date', 'created_at']

