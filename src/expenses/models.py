from datetime import datetime
from django.db import models
from django.db import transaction

from main.models import Year
from user.models import User

# Create your models here.

class ExpenseType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

class Expense(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.year:
            self.year = Year.current_year() or 0
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name + ' - ' + str(self.balance) + ' - ' + self.expense_type.name
    
    def record_payment(self, amount,description, payment_date):
        payment = ExpensePayment(expense=self, amount=amount,description=description, payment_date=payment_date)
        payment.save()

    

class ExpensePayment(models.Model):
    
        expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=10, decimal_places=2)
        description = models.TextField(null=True)
        bank = models.ForeignKey('bank.Bank', on_delete=models.CASCADE, null=True, blank=True)
        balance = models.DecimalField(max_digits=10, decimal_places=2)
        payment_date = models.DateField()
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_payments', null=True, blank=True)
        transaction = models.ForeignKey('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True)
        approved = models.BooleanField(default=False)
    
        def save(self, *args, **kwargs):
            super(ExpensePayment, self).save(*args, **kwargs)

            
        def __str__(self) -> str:
            return self.expense.name + ' - ' + str(self.amount)
