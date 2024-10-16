from django.db import models

from main.models import Year

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
    approved = models.BooleanField(default=False)

    def is_approved(self):
        return self.approved

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
        balance = models.DecimalField(max_digits=10, decimal_places=2)
        payment_date = models.DateField()
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        # create_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
        def save(self, *args, **kwargs):
            if not self.pk:
                self.balance = self.expense.balance
                self.expense.balance += self.amount
                self.expense.save()
            super(ExpensePayment, self).save(*args, **kwargs)
            
        def __str__(self) -> str:
            return self.expense.name + ' - ' + str(self.amount) + ' - ' + str(self.expense.balance)
