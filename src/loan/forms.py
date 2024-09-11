from .models import Loan, LoanPayment
from income.models import LoanRegistrationFee, RiskPremium, UnionContribution, LoanServiceFee

from django import forms

class LoanForm(forms.ModelForm):
    
    class Meta:
        model = Loan
        fields = '__all__'


class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = '__all__'

class LoanRegistrationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'interest', 'duration', 'start_date']