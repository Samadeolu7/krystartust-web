from django import forms
from django.forms import ModelForm, inlineformset_factory

from bank.models import Bank
from bank.utils import get_user_and_office_banks
from main.models import Year
from .models import Expense, ExpensePayment, ExpensePaymentBatch, ExpensePaymentBatchItem, ExpenseType


class ExpenseForm(ModelForm):

    year = Year.current_year()
    class Meta:
        model = Expense
        fields = ['name','description','balance_bf','expense_type']

class ExpensePaymentForm(ModelForm):
    year = Year.current_year()
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')
    expense = forms.ModelChoiceField(queryset=Expense.objects.filter(year=year), label='Expense')
    class Meta:
        model = ExpensePayment
        fields = ['expense', 'amount','payment_date','description','bank']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the user from kwargs
        super(ExpensePaymentForm, self).__init__(*args, **kwargs)

        # Filter the bank queryset
        if self.user:
            is_admin = self.user.groups.filter(name='Admin').exists()
            if not is_admin:
                self.fields['bank'].queryset = get_user_and_office_banks(self.user)
                  
class ExpenseTypeForm(ModelForm):
    class Meta:
        model = ExpenseType
        fields = ['name','description']


class ExpensePaymentBatchForm(forms.ModelForm):
    year = Year.current_year()

    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')
    class Meta:
        model = ExpensePaymentBatch
        fields = ['bank', 'description', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'class': 'description-box'}),
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ExpensePaymentBatchForm, self).__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            is_admin = self.user.groups.filter(name='Admin').exists()
            if not is_admin:
                # Get the banks associated with the user and office
                self.fields['bank'].queryset = get_user_and_office_banks(self.user)

class ExpensePaymentBatchItemForm(forms.ModelForm):
    year = Year.current_year()
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
