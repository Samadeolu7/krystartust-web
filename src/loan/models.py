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

    def is_defaulted(self):
        schedules = self.loanrepaymentschedule_set.all()
        for schedule in schedules:
            if schedule.due_date < date.today() and not schedule.is_paid:
                return True
        return False
    
    def __str__(self) -> str:
        return self.client.name + ' - ' + str(self.balance)


class LoanPayment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.FloatField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_schedule = models.ForeignKey('LoanRepaymentSchedule', on_delete=models.CASCADE)
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # create_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_payment = LoanPayment.objects.filter(client=self.client).order_by('-created_at').first()
            if last_payment:
                self.balance = last_payment.balance - self.amount
                # update loan balance
                self.loan.balance = self.balance
                self.loan.save()
            else:
                self.balance = self.amount
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.client.name + ' - ' + str(self.amount) + ' - ' + str(self.balance)


class LoanRepaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.loan.client.name + ' - ' + str(self.amount_due) + ' - ' + str(self.due_date)