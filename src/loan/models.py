from django.db import models
from client.models import Client
from datetime import date

# Create your models here.
class Loan(models.Model):
    LOAN_TYPE = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly')
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest = models.FloatField()
    loan_type = models.CharField(max_length=100, choices=LOAN_TYPE)
    duration = models.IntegerField()
    risk_premium = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    emi = models.FloatField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_defaulted(self):
        return self.repayment_schedule.filter(due_date__lt=date.today(), is_paid=False).exists()

    def __str__(self) -> str:
        return f"{self.client.name} - {self.balance}"
    

class LoanPayment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payment', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_schedule = models.ForeignKey('LoanRepaymentSchedule', on_delete=models.CASCADE)
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # create_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            balance = self.loan.balance
            if balance :
                self.balance = balance - self.amount
                # update loan balance
                self.loan.balance = self.balance
                self.loan.save()
            else:
                self.balance = -self.amount
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.client.name + ' - ' + str(self.amount) + ' - ' + str(self.balance)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']


class LoanRepaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayment_schedule', db_index=True)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.loan.client.name + ' - ' + str(self.amount_due) + ' - ' + str(self.due_date)