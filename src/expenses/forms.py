from django import forms
from django.forms import ModelForm, inlineformset_factory

from bank.models import Bank
from main.models import Year
from .models import Expense, ExpensePayment, ExpensePaymentBatch, ExpensePaymentBatchItem, ExpenseType

year = Year.current_year()
class ExpenseForm(ModelForm):

    class Meta:
        model = Expense
        fields = ['name','description','balance_bf','expense_type']

class ExpensePaymentForm(ModelForm):
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')
    expense = forms.ModelChoiceField(queryset=Expense.objects.filter(year=year), label='Expense')
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

    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')
    class Meta:
        model = ExpensePaymentBatch
        fields = ['bank', 'description', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'class': 'description-box'}),
        }

class ExpensePaymentBatchItemForm(forms.ModelForm):

    expense = forms.ModelChoiceField(queryset=Expense.objects.filter(year=year), label='Expense')
    class Meta:
        model = ExpensePaymentBatchItem
        fields = ['expense', 'amount', 'description']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'class': 'description-box'}),
        }
        

ExpensePaymentBatchItemFormSet = inlineformset_factory(
    ExpensePaymentBatch, ExpensePaymentBatchItem, form=ExpensePaymentBatchItemForm, extra=1, can_delete=True
)
