from datetime import datetime
from django.db import models
from django.db import transaction

from bank.models import BankPayment
from bank.utils import create_bank_payment
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
    
    def record_payment(self, amount,description, payment_date,transaction):
        payment = ExpensePayment(
            expense=self, amount=amount,description=description, payment_date=payment_date, approved=True,transaction=transaction, balance=self.balance + amount)
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
            
            with transaction.atomic():
                if not self.pk:
                    self.expense_balance = self.expense.balance + self.amount
                    self.expense.balance = self.expense_balance
                    self.expense.save()
            
            super(ExpensePayment, self).save(*args, **kwargs)

            
        def __str__(self) -> str:
            return self.expense.name + ' - ' + str(self.amount)

class ExpensePaymentBatch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_payment_batches')
    bank = models.ForeignKey('bank.Bank', on_delete=models.CASCADE)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True)
    approved = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    payment_date = models.DateField()

    def approve(self, approved_by):
        with transaction.atomic():
            total = 0
            for batch_item in self.batch_items.all():
                batch_item.create_expense_payment()
                total += batch_item.amount
            create_bank_payment(
                bank=self.bank,
                description=self.description,
                amount=total,
                payment_date=self.payment_date,
                transaction=self.transaction,
                created_by=approved_by
            )

    def __str__(self) -> str:
        return f"Batch {self.id} - Approved: {self.approved}"

class ExpensePaymentBatchItem(models.Model):
    batch = models.ForeignKey(ExpensePaymentBatch, on_delete=models.CASCADE, related_name='batch_items')
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True) 

    def create_expense_payment(self):
        ExpensePayment.objects.create(
            expense=self.expense,
            amount=self.amount,
            description=self.description,
            payment_date=self.batch.payment_date,
            transaction=self.batch.transaction,
            approved=True,
            balance=self.expense.balance + self.amount
        )
