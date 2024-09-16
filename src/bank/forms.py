from django.forms import ModelForm

from .models import Bank, BankPayment

class BankForm(ModelForm):
    class Meta:
        model = Bank
        fields = ['name','description','balance_bf']

class BankPaymentForm(ModelForm):
    class Meta:
        model = BankPayment
        fields = ['bank', 'payment_date', 'amount', 'description']