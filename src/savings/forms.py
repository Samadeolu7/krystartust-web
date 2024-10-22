from administration.models import Transaction
from bank.models import Bank
from loan.models import Loan, LoanPayment
from .models import SavingsPayment, CompulsorySavings, Savings
from loan.models import LoanRepaymentSchedule as PaymentSchedule

from django import forms

class CompulsorySavingsForm(forms.ModelForm):
    class Meta:
        model = CompulsorySavings
        fields = ['amount']

class SavingsExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File'
    )

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = SavingsPayment
        fields = ['savings', 'balance', 'amount', 'payment_date', 'transaction_type', 'description', 'bank']

    def __init__(self, *args, **kwargs):
        super(WithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'W'

    def save(self, commit=True):
        instance = super(SavingsForm, self).save(commit=False)
        if self.user:
            #instance.created_by = self.user
            instance.balance = instance.savings.balance - instance.amount
            instance.transaction_type = SavingsPayment.WITHDRAWAL
        if commit:
            instance.save()
        return instance

class SavingsForm(forms.ModelForm):
    bank = forms.ModelChoiceField(queryset=Bank.objects.all(), required=False)
    class Meta:
        model = SavingsPayment
        fields = ['savings', 'amount', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SavingsForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(SavingsForm, self).save(commit=False)
        instance.client = instance.savings.client
        if self.user:
            #instance.created_by = self.user
            instance.balance = instance.savings.balance + instance.amount
            instance.transaction_type = SavingsPayment.SAVINGS
        if commit:
            instance.save()
        return instance

# class SavingsPayment(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     savings = models.ForeignKey(Savings, on_delete=models.CASCADE)
#     balance = models.DecimalField(max_digits=10, decimal_places=2)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     #created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class CombinedPaymentForm(forms.ModelForm):
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    bank = forms.ModelChoiceField(queryset=Bank.objects.all(), required=False)
    payment_schedule = forms.ModelChoiceField(queryset=PaymentSchedule.objects.none(), required=False)
    amount = forms.DecimalField(required=False)

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )

    class Meta:
        model = LoanPayment
        fields = ['client', 'payment_schedule', 'payment_date']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                loan = Loan.objects.get(client=client_id)
                savings = Savings.objects.get(client=client_id)
                self.fields['payment_schedule'].queryset = PaymentSchedule.objects.filter(loan=loan).order_by('due_date')
                self.instance.loan = loan
                self.instance.savings = savings
                
                
            except (ValueError, TypeError, Loan.DoesNotExist):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['payment_schedule'].queryset = self.instance.loan.client.paymentschedule_set.order_by('due_date')

    def save(self, commit=True):
        loan_payment_instance = super().save(commit=False)
        savings_payment_instance = SavingsPayment()

        # Handle loan payment
        if self.cleaned_data['payment_date']:
            tran = Transaction(description=f'Loan payment from {loan_payment_instance.loan.client.name}')
            tran.save(prefix='LOA')
            loan_payment_instance.transaction = tran
            loan_payment_instance.payment_date = self.cleaned_data['payment_date']
            loan_payment_instance.client = loan_payment_instance.loan.client
            loan_payment_instance.amount = loan_payment_instance.loan.emi
            loan_payment_instance.payment_schedule.is_paid = True
            loan_payment_instance.payment_schedule.payment_date = loan_payment_instance.payment_date
            loan_payment_instance.payment_schedule.save()
            if self.user:
                loan_payment_instance.created_by = self.user
            if commit:
                loan_payment_instance.save()

        # Handle savings payment
        if self.cleaned_data['payment_date']:
            tran = Transaction(f'Savings payment from {loan_payment_instance.loan.client.name}')
            tran.save(prefix='SAV')
            savings_payment_instance.transaction = tran
            savings_payment_instance.client = self.cleaned_data['client']
            savings_payment_instance.amount = self.cleaned_data['amount']-loan_payment_instance.amount
            savings_payment_instance.payment_date = self.cleaned_data['payment_date']
            savings_payment_instance.client = loan_payment_instance.savings.client
            if self.user:
                savings_payment_instance.created_by = self.user
            savings_payment_instance.transaction_type = SavingsPayment.SAVINGS
            if commit:
                savings_payment_instance.save()

        return loan_payment_instance, savings_payment_instance