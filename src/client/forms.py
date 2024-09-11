from django import forms
from .models import Client
from income.models import RegistrationFee
from savings.models import CompulsorySavings
from bank.models import Bank

class ClientForm(forms.ModelForm):
    compulsory_savings = forms.DecimalField(
        label='Compulsory Savings',
        disabled=True,
        required=False
    )
    registration_fee = forms.DecimalField(
        label='Registration Fee',
        disabled=True,
        required=False
    )
    bank = forms.ModelChoiceField(
        queryset=Bank.objects.all(),
        required=False
    )

    class Meta:
        model = Client
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['compulsory_savings'].initial = CompulsorySavings.objects.filter(client=self.instance).first().amount
            self.fields['registration_fee'].initial = RegistrationFee.objects.filter(client=self.instance).first().amount