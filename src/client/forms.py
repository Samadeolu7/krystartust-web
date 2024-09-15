from django import forms
from .models import Client
from income.models import RegistrationFee
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
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.all(),
    )

    class Meta:
        model = Client
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['compulsory_savings'].initial = CompulsorySavings.objects.all().first().amount
        self.fields['registration_fee'].initial = RegistrationFee.objects.all().first().amount
        self.fields['compulsory_savings'].widget.attrs['readonly'] = True
        self.fields['registration_fee'].widget.attrs['readonly'] = True