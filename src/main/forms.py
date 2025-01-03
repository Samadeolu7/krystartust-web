# forms.py
from django import forms
from .models import ClientGroup as Group
from expenses.models import Expense
from income.models import Income
from bank.models import Bank
from liability.models import Liability
from bank.models import BankPayment
from django.forms import ModelForm


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
    
class JVForm(forms.Form):
    choices = [('Income', 'Income'), ('Expense', 'Expense'), ('Liability', 'Liability'), ('Bank', 'Bank')]
    jv_credit = forms.ChoiceField(choices=choices, label="Credit Type")
    jv_credit_account = forms.ModelChoiceField(queryset=Expense.objects.none(), label="Credit Account")
    jv_debit = forms.ChoiceField(choices=choices, label="Debit Type")
    jv_debit_account = forms.ModelChoiceField(queryset=Expense.objects.none(), label="Debit Account")
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2030)))
    description = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jv_credit_account'].queryset = Expense.objects.none()
        self.fields['jv_debit_account'].queryset = Expense.objects.none()

        if 'jv_credit' in self.data:
            self._update_account_queryset('jv_credit', 'jv_credit_account')
        if 'jv_debit' in self.data:
            self._update_account_queryset('jv_debit', 'jv_debit_account')

    def _update_account_queryset(self, type_field, account_field):
        type_value = self.data.get(type_field)
        if type_value == 'Income':
            self.fields[account_field].queryset = Income.objects.all()
        elif type_value == 'Expense':
            self.fields[account_field].queryset = Expense.objects.all()
        elif type_value == 'Liability':
            self.fields[account_field].queryset = Liability.objects.all()
        elif type_value == 'Bank':
            self.fields[account_field].queryset = Bank.objects.all() 
