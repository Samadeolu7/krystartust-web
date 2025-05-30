from datetime import datetime
from django import forms

from main.models import ClientGroup, Year
from .models import Client, Prospect
from income.models import RegistrationFee, IDFee
from savings.models import CompulsorySavings
from bank.models import Bank



class ClientForm(forms.ModelForm):
    year = Year.current_year()
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
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')

    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Client
        fields = ['name', 'client_type', 'email', 'phone', 'address', 'group', 'marital_status', 'next_of_kin', 'next_of_kin_phone', 'bank_name', 'account_number', 'date']

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['compulsory_savings'].initial = CompulsorySavings.objects.all().first().amount
        self.fields['registration_fee'].initial = RegistrationFee.objects.all().first().amount
        self.fields['id_fee'].initial = IDFee.objects.all().first().amount
        self.fields['date'].initial = datetime.now().date()

class ProspectForm(forms.ModelForm):
    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.now().date()
    )
    loan_amount = forms.DecimalField(
        label='Loan Amount',
        required=False
    )
    loan_type = forms.ChoiceField(
        label='Loan Type',
        choices=[
            ('WL', 'Weekly Loan'),
            ('ML', 'Monthly Loan'),
            ('BL', 'Business Loan'),
        ],
        required=False
    )

    class Meta:
        model = Client
        fields = ['name', 'phone', 'date']

    def save(self, user, commit = True):
        # Add the prospect to the "Prospect" group
        instance = super().save(commit=False)
        prospect_group, _ = ClientGroup.objects.get_or_create(name='Prospect')
        instance.group = prospect_group
        instance.client_type = 'PR'
        instance.account_status = Client.PROSPECT  # Set status to "Prospect"
        instance.created_at = datetime.now()
        instance.updated_at = datetime.now()

        if commit:
            instance.save()
            Prospect.objects.create(
                client=instance,
                loan_amount=self.cleaned_data['loan_amount'],
                loan_type=self.cleaned_data['loan_type'],
                created_by=user
            )
        return instance