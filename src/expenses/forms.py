from django import forms
from django.forms import ModelForm, inlineformset_factory

from bank.models import Bank
from .models import Expense, ExpensePayment, ExpensePaymentBatch, ExpensePaymentBatchItem, ExpenseType

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


class ExpensePaymentBatchForm(forms.ModelForm):
    class Meta:
        model = ExpensePaymentBatch
        fields = ['bank', 'description']

class ExpensePaymentBatchItemForm(forms.ModelForm):
    class Meta:
        model = ExpensePaymentBatchItem
        fields = ['expense', 'amount', 'description', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

ExpensePaymentBatchItemFormSet = inlineformset_factory(
    ExpensePaymentBatch, ExpensePaymentBatchItem, form=ExpensePaymentBatchItemForm, extra=1, can_delete=True
)
