from django.db import models

# Create your models here.

class ExpenseType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

class Expense(models.Model):

    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE, related_name='expenses')
    duration = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name + ' - ' + str(self.amount) + ' - ' + self.expense_type
    

class ExpensePayment(models.Model):
    
        expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
        amount = models.FloatField()
        payment_date = models.DateField()
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        # create_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
        def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            self.expense.balance = self.expense.balance - self.amount
            self.expense.save()

        def __str__(self) -> str:
            return self.expense.name + ' - ' + str(self.amount) + ' - ' + str(self.expense.balance)
