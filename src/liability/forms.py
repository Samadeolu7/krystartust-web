from django.forms import ModelForm
from .models import Liability, LiabilityPayment

class LiabilityForm(ModelForm):
    class Meta:
        model = Liability
        fields = ['name','description','balance_bf']

class LiabilityPaymentForm(ModelForm):
    class Meta:
        model = LiabilityPayment
        fields = ['liability', 'payment_date', 'amount']
                  

# forms.py    