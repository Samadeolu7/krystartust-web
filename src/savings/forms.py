from .models import SavingsPayment, CompulsorySavings, Savings

from django import forms

class CompulsorySavingsForm(forms.ModelForm):
    class Meta:
        model = CompulsorySavings
        fields = ['amount']

class SavingsForm(forms.ModelForm):
    class Meta:
        model = SavingsPayment
        fields = ['client', 'amount']

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = SavingsPayment
        fields = ['client', 'savings', 'balance', 'amount', 'payment_date', 'transaction_type']

    def __init__(self, *args, **kwargs):
        super(WithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'W'

    def save(self, commit=True):
        instance = super(SavingsForm, self).save(commit=False)
        if self.user:
            #instance.created_by = self.user
            instance.balance = instance.savings.balance - instance.amount
            instance.transaction_type = SavingsPayment.WITHDRAWAL
        if commit:
            instance.save()
        return instance

class SavingsForm(forms.ModelForm):
    class Meta:
        model = SavingsPayment
        fields = ['client', 'savings', 'balance', 'amount', 'payment_date']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SavingsForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(SavingsForm, self).save(commit=False)
        if self.user:
            #instance.created_by = self.user
            instance.balance = instance.savings.balance + instance.amount
            instance.transaction_type = SavingsPayment.SAVINGS
        if commit:
            instance.save()
        return instance

# class SavingsPayment(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     savings = models.ForeignKey(Savings, on_delete=models.CASCADE)
#     balance = models.DecimalField(max_digits=10, decimal_places=2)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     #created_by = models.ForeignKey(User, on_delete=models.CASCADE)