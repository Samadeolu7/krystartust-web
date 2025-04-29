from bank.models import Bank
from bank.utils import get_user_and_office_banks
from client.models import Client
from main.models import Year
from savings.models import Savings
from .models import Loan, LoanPayment, LoanRepaymentSchedule as PaymentSchedule, Guarantor
from income.models import LoanRegistrationFee, RiskPremium, UnionContribution, LoanServiceFee
from django_select2.forms import Select2Widget

from django import forms


class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = '__all__'

class LoanPaymentForm(forms.ModelForm):
    year = Year.current_year()
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')
    payment_schedule = forms.ModelChoiceField(queryset=PaymentSchedule.objects.none())

    class Meta:
        model = LoanPayment
        fields = ['loan', 'amount', 'payment_schedule', 'payment_date']
        widgets = { 'loan': Select2Widget}

    def __init__(self, *args, **kwargs):
        # Get the user from kwargs
        self.user = kwargs.pop('user', None)  # Get the user from kwargs
        super(LoanPaymentForm, self).__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            self.fields['bank'].queryset = get_user_and_office_banks(self.user)
        super().__init__(*args, **kwargs)
        if 'loan' in self.data:
            try:
                loan_id = int(self.data.get('loan'))
                loan = Loan.objects.get(id=loan_id)
                self.fields['payment_schedule'].queryset = PaymentSchedule.objects.filter(loan=loan).order_by('due_date')
            except (ValueError, TypeError, Loan.DoesNotExist):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['payment_schedule'].queryset = self.instance.loan.client.paymentschedule_set.order_by('due_date')

class LoanRegistrationForm(forms.ModelForm):
    year = Year.current_year()
    registration_fee = forms.DecimalField(
        label='Loan Form Fee',
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
    admin_fees = forms.DecimalField(
        label='Admin Fees',
        required=False
    )
    interest = forms.DecimalField(
        label='Interest',
        required=False
    )
    sms_fees = forms.DecimalField(
        label='SMS Fees',
        required=False
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=year), label='Bank')
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'duration','loan_type','interest', 'bank', 'start_date', 'registration_fee', 'risk_premium']
        widgets = { 'client': Select2Widget, }

    def __init__(self, *args, **kwargs):
        # Get the user from kwargs
        self.user = kwargs.pop('user', None)  # Get the user from kwargs

        super(LoanRegistrationForm, self).__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            self.fields['bank'].queryset = get_user_and_office_banks(self.user)
        self.fields['registration_fee'].initial = LoanRegistrationFee.objects.all().first().amount
        self.fields['risk_premium'].initial = RiskPremium.objects.all().first().amount
        self.fields['union_contribution'].initial = UnionContribution.objects.all().first().amount
        self.fields['interest'].initial = LoanServiceFee.objects.all().first().amount


class LoanExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File'
    )

class LoanUploadForm(forms.Form):
    file = forms.FileField(label='Select an Excel file')

class LoanPaymentFromSavingsForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), widget=Select2Widget)
    loan = forms.ModelChoiceField(queryset=Loan.objects.none(), widget=Select2Widget)
    payment_schedule = forms.ModelChoiceField(queryset=PaymentSchedule.objects.none())
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False, disabled=True)
    savings_balance = forms.DecimalField(max_digits=10, decimal_places=2, required=False, disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['loan'].queryset = Loan.objects.filter(client_id=client_id)
                self.fields['savings_balance'].initial = Savings.objects.get(client_id=client_id).balance
            except (ValueError, TypeError, Savings.DoesNotExist):
                pass
        if 'loan' in self.data:
            try:
                loan_id = int(self.data.get('loan'))
                self.fields['payment_schedule'].queryset = PaymentSchedule.objects.filter(loan_id=loan_id, is_paid=False)
            except (ValueError, TypeError):
                pass