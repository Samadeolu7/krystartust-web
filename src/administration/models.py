from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from bank.utils import create_bank_payment, get_cash_in_hand
from user.models import User
import uuid

# Create your models here.

class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    bank_name = models.CharField(max_length=100,blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    transportation = models.DecimalField(max_digits=10, decimal_places=2)
    food = models.DecimalField(max_digits=10, decimal_places=2)
    house_rent = models.DecimalField(max_digits=10, decimal_places=2)
    utility = models.DecimalField(max_digits=10, decimal_places=2)
    entertainment = models.DecimalField(max_digits=10, decimal_places=2)
    leave = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nhf = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    absent_days = models.IntegerField(default=0)
    prorated_days = models.IntegerField(default=0)
    attendance_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    absent_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prorated_days_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    private_loan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pension = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username


class Approval(models.Model):
    Expenses = 'expenses'
    Batch_Expense = 'batch_expense'
    Loan = 'loan'
    Withdrawal = 'withdrawal'
    Salary = 'salary'
    TYPES = (
        ('Expenses', Expenses),
        ('Batch_Expense', Batch_Expense),
        ('Loan', Loan),
        ('Withdrawal', Withdrawal),
        ('Salary', Salary)
    )
    type = models.CharField(max_length=100, choices=TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals', null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.comment = f"{self.user.username} requested approval for {self.type} for {self.content_object}"
            super().save(*args, **kwargs)
        else:
            if self.approved:
                if self.type == self.Withdrawal:
                    savings_payment = self.content_object
                    savings = savings_payment.savings
                    create_bank_payment(
                        bank=savings_payment.bank,
                        description=f"Withdrawal by {savings.client.name}",
                        amount=savings_payment.amount,
                        payment_date=savings_payment.payment_date,
                        transaction=savings_payment.transaction,
                        created_by=savings_payment.created_by
                    )
                
                self.content_object.approved = True
                self.content_object.save()
                super().save(*args, **kwargs)
            elif self.rejected:
                objmodel = self.content_object
                if objmodel:
                    objmodel.save()
                super().save(*args, **kwargs)
                # Delete the related object if it still exists
                if objmodel:
                    self.content_object.delete()
            else:
                super().save(*args, **kwargs)


class Transaction(models.Model):
    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', 'TRN')
        if not self.reference_number:
            self.reference_number = self.generate_reference_number(prefix)
        super().save(*args, **kwargs)

    def generate_reference_number(self, prefix='TRN'):
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        unique_part = str(uuid.uuid4())[:5].upper()
        return f"{prefix}-{unique_part}{current_month:02d}{current_year}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    payslip_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
    

class MonthStatus(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"{self.month}/{self.year} - {'Closed' if self.is_closed else 'Open'}"