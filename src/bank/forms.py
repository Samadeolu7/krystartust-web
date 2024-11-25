from django.forms import ModelForm
from django import forms

from administration.utils import validate_month_status
from .models import Bank, BankPayment

class BankForm(ModelForm):
    class Meta:
        model = Bank
        fields = ['name','description','balance_bf']

class BankPaymentForm(ModelForm):
    class Meta:
        model = BankPayment
        fields = ['bank', 'payment_date', 'amount', 'description']

class CashTransferForm(forms.Form):
    source_bank = forms.ModelChoiceField(queryset=Bank.objects.all(), label="Source Bank")
    destination_bank = forms.ModelChoiceField(queryset=Bank.objects.all(), label="Destination Bank")
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    description = forms.CharField(widget=forms.Textarea, required=False)
    payment_date = forms.DateField(widget=forms.SelectDateWidget)


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
