from django.urls import reverse
from django.db import models

# Create your models here.

class Liability(models.Model):
    name = models.CharField(max_length=100)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name- self.amount

    def get_absolute_url(self):
        return reverse('liability:liability_detail', kwargs={'pk': self.pk})
    

class LiabilityPayment(models.Model):
    liability = models.ForeignKey(Liability, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.liability.name
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.liability.balance -= self.amount
            self.liability.save()
        super(LiabilityPayment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('liability:liability_record_detail', kwargs={'pk': self.pk})