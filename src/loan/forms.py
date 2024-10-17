from bank.models import Bank
from .models import Loan, LoanPayment, LoanRepaymentSchedule as PaymentSchedule, Guarantor
from income.models import LoanRegistrationFee, RiskPremium, UnionContribution, LoanServiceFee

from django import forms

class LoanForm(forms.ModelForm):

    registration_fee = forms.DecimalField(
        label='Registration Fee',
        disabled=True,
        required=False
    )
    risk_premium = forms.DecimalField(
        label='Risk Premium',
        disabled=True,
        required=False
    )
    union_contribution = forms.DecimalField(
        label='Union Contribution',
        disabled=True,
        required=False
    )
    service_fee = forms.DecimalField(
        label='Service Fee',
        disabled=True,
        required=False
    )
    
    class Meta:
        model = Loan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['registration_fee'].initial = LoanRegistrationFee.objects.filter(loan=self.instance).first().amount
            self.fields['risk_premium'].initial = RiskPremium.objects.filter(loan=self.instance).first().amount
            self.fields['union_contribution'].initial = UnionContribution.objects.filter(loan=self.instance).first().amount
            self.fields['service_fee'].initial = LoanServiceFee.objects.filter(loan=self.instance).first().amount


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
    bank = forms.ModelChoiceField(queryset=Bank.objects.all())
    start_date = forms.DateField(
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Loan
        fields = ['client', 'amount', 'duration','loan_type','interest', 'bank', 'start_date', 'registration_fee', 'risk_premium']

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