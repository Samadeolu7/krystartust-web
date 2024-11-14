from bank.models import Bank
from .models import Loan, LoanPayment, LoanRepaymentSchedule as PaymentSchedule, Guarantor
from income.models import LoanRegistrationFee, RiskPremium, UnionContribution, LoanServiceFee
from django_select2.forms import Select2Widget

from django import forms


class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = '__all__'

class LoanPaymentForm(forms.ModelForm):
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    payment_schedule = forms.ModelChoiceField(queryset=PaymentSchedule.objects.none())

    class Meta:
        model = LoanPayment
        fields = ['loan', 'amount', 'payment_schedule', 'payment_date']

    def __init__(self, *args, **kwargs):
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

    registration_fee = forms.DecimalField(
        label='Registration Fee',
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
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'duration','loan_type','interest', 'bank', 'start_date', 'registration_fee', 'risk_premium']
        widgets = { 'client': Select2Widget, }

    def __init__(self, *args, **kwargs):
        super(LoanRegistrationForm, self).__init__(*args, **kwargs)
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