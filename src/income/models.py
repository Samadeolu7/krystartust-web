from django.db import models
from user.models import User

class Income(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_bf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.IntegerField()

    def __str__(self):
        return f'{self.name} - {self.description}'
    
    class Meta:
        ordering = ['created_at']

    def record_payment(self, amount,description, payment_date):
        payment = IncomePayment(income=self, amount=amount,description=description, payment_date=payment_date)
        payment.save()

class IncomePayment(models.Model):
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    income_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_payments', null=True, blank=True)
    transaction = models.ForeignKey('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True)
    payment_date = models.DateField()

    def __str__(self):
        return f'{self.income.name} - {self.amount}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.income_balance = self.income.balance + self.amount
            self.income.balance = self.income_balance
            self.income.save()
        super(IncomePayment, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['created_at']

class SingletonModel(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class RegistrationFee(SingletonModel):
    def __str__(self):
        return f'Registration Fee - {self.amount}'

class IDFee(SingletonModel):
    def __str__(self):
        return f'ID Fee - {self.amount}'

class LoanRegistrationFee(SingletonModel):
    def __str__(self):
        return f'Loan Registration Fee - {self.amount}'

class RiskPremium(SingletonModel):
    def __str__(self):
        return f'Risk Premium - {self.amount}%'

class UnionContribution(SingletonModel):
    def __str__(self):
        return f'Union Contribution - {self.amount}'

class LoanServiceFee(SingletonModel):
    def __str__(self):
        return f'Loan Service Fee - {self.amount}%'