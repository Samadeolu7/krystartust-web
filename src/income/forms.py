from django import forms

from .models import RegistrationFee, IDFee, LoanRegistrationFee, RiskPremium, UnionContribution, LoanServiceFee

class RegistrationFeeForm(forms.ModelForm):
    class Meta:
        model = RegistrationFee
        fields = '__all__'

class IDFeeForm(forms.ModelForm):
    class Meta:
        model = IDFee
        fields = '__all__'

class LoanRegistrationFeeForm(forms.ModelForm):
    class Meta:
        model = LoanRegistrationFee
        fields = '__all__'

class RiskPremiumForm(forms.ModelForm):
    class Meta:
        model = RiskPremium
        fields = '__all__'

class UnionContributionForm(forms.ModelForm):
    class Meta:
        model = UnionContribution
        fields = '__all__'

class LoanServiceFeeForm(forms.ModelForm):
    class Meta:
        model = LoanServiceFee
        fields = '__all__'