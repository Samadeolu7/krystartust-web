from django.urls import reverse
from django.db import models

from main.models import Year

# Create your models here.

class Liability(models.Model):
    name = models.CharField(max_length=100)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    year = models.IntegerField(default=2024)
    def __str__(self):
        return f'{self.name} - {self.balance}'

    def get_absolute_url(self):
        return reverse('liability:liability_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.year:
            self.year = Year.current_year() or 0
        super().save(*args, **kwargs)

    def record_payment(self, amount,description, payment_date):
        payment = LiabilityPayment(liability=self, amount=amount,description=description, payment_date=payment_date)
        payment.save()
    

class LiabilityPayment(models.Model):
    liability = models.ForeignKey(Liability, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null =True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.liability.name
    
    def save(self, *args, **kwargs):
        if not self.pk:
            last_payment = LiabilityPayment.objects.filter(liability=self.liability).order_by('-payment_date', '-created_at').first()
            balance = last_payment.balance if last_payment else 0
            if balance:
                self.balance = balance + self.amount
                self.liability.balance = self.balance
                self.liability.save()
            else:
                self.balance = self.amount

        super(LiabilityPayment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('liability:liability_record_detail', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['-payment_date', '-created_at']