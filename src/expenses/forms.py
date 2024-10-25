from django import forms
from django.forms import ModelForm

from bank.models import Bank
from .models import Expense, ExpensePayment, ExpenseType

class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name','description','balance_bf','expense_type']

class ExpensePaymentForm(ModelForm):

    class Meta:
        model = ExpensePayment
        fields = ['expense', 'amount','payment_date','description','bank']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
                  
class ExpenseTypeForm(ModelForm):
    class Meta:
        model = ExpenseType
        fields = ['name','description']


# forms.py    