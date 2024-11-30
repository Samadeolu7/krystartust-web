from decimal import Decimal
from django.db import models
from django.utils import timezone

from user.models import User
from main.models import Year


def recalculate_balance_after_payment_date(bank_id, payment_date):
    payments = BankPayment.objects.filter(bank_id=bank_id, payment_date__gt=payment_date).order_by('payment_date', 'created_at')
    
    last_payment = BankPayment.objects.filter(bank_id=bank_id, payment_date__lte=payment_date).order_by('-payment_date', '-created_at').first()
    previous_balance = last_payment.bank_balance if last_payment else Decimal('0.00')

    updates = []
    for payment in payments:
        payment.bank_balance = previous_balance + payment.amount
        previous_balance = payment.bank_balance
        updates.append(payment)

    BankPayment.objects.bulk_update(updates, ['bank_balance'])
        
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
    
    def record_payment(self, amount, description,payment_date,transaction):
        payment = BankPayment(bank=self, amount=amount,description=description, payment_date=payment_date,transaction=transaction)
        payment.save()
    class Meta:
        ordering = ['created_at']

class BankPayment(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='payments', db_index=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bank_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_payments', null=True, blank=True)
    payment_date = models.DateField()

    def __str__(self):
        return f'{self.bank.name} - {self.amount}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # Find the last transaction before the payment date
            last_payment = BankPayment.objects.filter(bank=self.bank, payment_date__lt=self.payment_date).order_by('-payment_date', '-created_at').first()
            if last_payment:
                self.bank_balance = last_payment.bank_balance + self.amount
            else:
                self.bank_balance = self.amount  # If no previous payment, start with the amount

            self.bank.balance += self.amount
            self.bank.save()
        
        super(BankPayment, self).save(*args, **kwargs)

        # Check if the payment date is not today and trigger recalculation
        if self.payment_date != timezone.now().date():
            recalculate_balance_after_payment_date(self.bank.id, self.payment_date)

    def delete(self, *args, **kwargs):
        self.bank.balance -= self.amount
        self.bank.save()
        super(BankPayment, self).delete(*args, **kwargs)
    
    class Meta:
        ordering = ['payment_date', 'created_at']
        indexes = [
            models.Index(fields=['payment_date'], name='idx_payment_date'),
            models.Index(fields=['payment_date', 'created_at'], name='idx_payment_date_created_at'),
            models.Index(fields=['created_by'], name='idx_created_by'),
        ]

