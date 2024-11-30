from django.urls import reverse
from django.db import models

from main.models import Year

# Create your models here.

class Liability(models.Model):
    name = models.CharField(max_length=100)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    year = models.IntegerField(default=2024)
    def __str__(self):
        return f'{self.name} - {self.balance}'

    def get_absolute_url(self):
        return reverse('liability_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.year:
            self.year = Year.current_year() or 0
        super().save(*args, **kwargs)

    def record_payment(self, amount,description, payment_date,transaction):
        payment = LiabilityPayment(liability=self, amount=amount,description=description, payment_date=payment_date,transaction=transaction)
        payment.save()
    

class LiabilityPayment(models.Model):
    liability = models.ForeignKey(Liability, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null =True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True, related_name='liability_payments')
    created_by = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='liability_payments', null=True, blank=True)

    def __str__(self):
        return self.liability.name
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            balance = self.liability.balance

            self.balance = balance + self.amount
            self.liability.balance = self.balance
            self.liability.save()

        super(LiabilityPayment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        balance = self.liability.balance
        self.liability.balance = balance - self.amount
        self.liability.save()
        super(LiabilityPayment, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('liability_detail', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['payment_date', 'created_at']