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

    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    class Meta:
        model = LoanPayment
        fields = ['client', 'amount', 'payment_schedule', 'payment_date', 'loan']

class LoanRegistrationForm(forms.ModelForm):

    registration_fee = forms.DecimalField(
        label='Registration Fee',
        required=False
    )
    risk_premium = forms.DecimalField(
        label='Risk Premium',
        required=False
    )
    union_contribution = forms.DecimalField(
        label='Union Contribution',
        required=False
    )
    interest = forms.DecimalField(
        label='Interest',
        required=False
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'duration','loan_type','interest', 'bank', 'start_date', 'registration_fee', 'risk_premium']

    def __init__(self, *args, **kwargs):
        super(LoanRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['registration_fee'].initial = LoanRegistrationFee.objects.all().first().amount
        self.fields['risk_premium'].initial = RiskPremium.objects.all().first().amount
        self.fields['union_contribution'].initial = UnionContribution.objects.all().first().amount
        self.fields['interest'].initial = LoanServiceFee.objects.all().first().amount
        self.fields['registration_fee'].widget.attrs['readonly'] = True
        self.fields['risk_premium'].widget.attrs['readonly'] = True
        self.fields['union_contribution'].widget.attrs['readonly'] = True
        self.fields['interest'].widget.attrs['readonly'] = True


class LoanExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File'
    )