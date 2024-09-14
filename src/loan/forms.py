from bank.models import Bank
from .models import Loan, LoanPayment
from income.models import LoanRegistrationFee, RiskPremium, UnionContribution, LoanServiceFee

from django import forms

class LoanForm(forms.ModelForm):

    registration_fee = forms.DecimalField(
        label='Registration Fee',
        disabled=True,
        required=False
    )
    risk_premium = forms.DecimalField(
        label='Risk Premium',
        disabled=True,
        required=False
    )
    union_contribution = forms.DecimalField(
        label='Union Contribution',
        disabled=True,
        required=False
    )
    service_fee = forms.DecimalField(
        label='Service Fee',
        disabled=True,
        required=False
    )
    
    class Meta:
        model = Loan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['registration_fee'].initial = LoanRegistrationFee.objects.filter(loan=self.instance).first().amount
            self.fields['risk_premium'].initial = RiskPremium.objects.filter(loan=self.instance).first().amount
            self.fields['union_contribution'].initial = UnionContribution.objects.filter(loan=self.instance).first().amount
            self.fields['service_fee'].initial = LoanServiceFee.objects.filter(loan=self.instance).first().amount


class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = '__all__'

class LoanRegistrationForm(forms.ModelForm):

    registration_fee = forms.DecimalField(
        label='Registration Fee',
        disabled=True,
        required=False
    )
    risk_premium = forms.DecimalField(
        label='Risk Premium',
        disabled=True,
        required=False
    )
    union_contribution = forms.DecimalField(
        label='Union Contribution',
        disabled=True,
        required=False
    )
    service_fee = forms.DecimalField(
        label='Service Fee',
        disabled=True,
        required=False
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'interest', 'duration', 'start_date']

    def __init__(self, *args, **kwargs):
        super(LoanRegistrationForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['registration_fee'].initial = LoanRegistrationFee.objects.filter(loan=self.instance).first().amount
            self.fields['risk_premium'].initial = RiskPremium.objects.filter(loan=self.instance).first().amount
            self.fields['union_contribution'].initial = UnionContribution.objects.filter(loan=self.instance).first().amount
            self.fields['service_fee'].initial = LoanServiceFee.objects.filter(loan=self.instance).first().amount