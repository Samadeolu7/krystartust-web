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



class ReversePaymentForm(forms.Form):
    type = forms.ChoiceField(choices=(('SVS','Savings'), ('LOA','Loan'), ('COM','Combined')), label='Type')
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    payment_date = forms.DateField(widget=forms.SelectDateWidget)
    payment = forms.ModelChoiceField(queryset=BankPayment.objects.none())
    reversal_date = forms.DateField(widget=forms.SelectDateWidget)
    reason = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment'].queryset = BankPayment.objects.none()
        if 'type' in self.data and 'bank' in self.data and 'payment_date_day' in self.data:
            try:
                type = self.data.get('type')
                print(type)
                bank_id = int(self.data.get('bank'))
                payment_date_day = self.data.get('payment_date_day')
                payment_date_month = self.data.get('payment_date_month')
                payment_date_year = self.data.get('payment_date_year')
                payment_date = f'{payment_date_year}-{payment_date_month}-{payment_date_day}'
                print(payment_date)
                self.fields['payment'].queryset = self.get_filtered_payments(type, bank_id, payment_date)
            except (ValueError, TypeError):
                pass
        else:
            print('No data')

    def get_filtered_payments(self, type, bank_id, payment_date):
        return BankPayment.objects.filter(
            bank=bank_id,
            payment_date=payment_date,
            transaction__reference_number__startswith=type[:3]
        )
    