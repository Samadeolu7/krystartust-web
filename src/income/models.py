from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Income(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.IntegerField()

    def __str__(self):
        return f'{self.client_id} - {self.amount}'
    
    class Meta:
        ordering = ['-created_at']

class IncomePayment(models.Model):
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    income_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateField()

    def __str__(self):
        return f'{self.client_id} - {self.amount}'
    
    def save(self, *args, **kwargs):
        self.income_balance = self.income.balance + self.amount
        self.income.balance = self.income_balance
        self.income.save()
        super(IncomePayment, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class RegistrationFee(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Registration Fee - {self.amount}'
    

class IDFee(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'ID Fee - {self.amount}'
    


class LoanRegistrationFee(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Loan Registration Fee - {self.amount}'
    

class RiskPremium(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Risk Premium - {self.amount}%'
    
class UnionContribution(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Union Contribution - {self.amount}'
    

class LoanServiceFee(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Loan Service Fee - {self.amount}%'
    

