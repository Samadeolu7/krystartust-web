from django import forms
from django.forms import ModelForm

from main.models import Year
from .models import Liability, LiabilityPayment

year = Year.current_year()
class LiabilityForm(ModelForm):
    class Meta:
        model = Liability
        fields = ['name','description','balance_bf']

class LiabilityPaymentForm(ModelForm):

    liability = forms.ModelChoiceField(queryset=Liability.objects.filter(year=year), label='Liability')
    class Meta:
        model = LiabilityPayment
        fields = ['liability', 'payment_date', 'amount']