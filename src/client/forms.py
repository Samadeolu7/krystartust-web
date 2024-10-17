from django import forms
from .models import Client
from income.models import RegistrationFee, IDFee
from savings.models import CompulsorySavings
from bank.models import Bank

class ClientForm(forms.ModelForm):
    compulsory_savings = forms.DecimalField(
        label='Compulsory Savings',
        required=False
    )
    registration_fee = forms.DecimalField(
        label='Registration Fee',
        required=False
    )
    id_fee = forms.DecimalField(
        label='ID Fee',
        required=False
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.all(), required=False)

    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'address', 'group', 'marital_status', 'next_of_kin', 'next_of_kin_phone', 'bank_name', 'account_number', 'date']

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['compulsory_savings'].initial = CompulsorySavings.objects.all().first().amount
        self.fields['registration_fee'].initial = RegistrationFee.objects.all().first().amount
        self.fields['id_fee'].initial = IDFee.objects.all().first().amount


class ClientExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File'
    )
    