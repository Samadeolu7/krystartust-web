import calendar
import datetime
from typing import Any
from administration.models import Transaction
from bank.models import Bank
from bank.utils import get_user_and_office_banks
from loan.models import Loan, LoanPayment
from main.models import ClientGroup, Year
from main.utils import verify_trial_balance
from savings.utils import create_dc_payment, setup_monthly_contributions
from .models import SavingsPayment, CompulsorySavings, Savings, DailyContribution, ClientContribution
from loan.models import LoanRepaymentSchedule as PaymentSchedule

from django_select2.forms import Select2Widget
from django.utils import timezone
from django.db import transaction
from django import forms


class CompulsorySavingsForm(forms.ModelForm):
    class Meta:
        model = CompulsorySavings
        fields = ['amount']

class SavingsExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File'
    )


class DCForm(forms.Form):
    queryset = ClientContribution.objects.all()
    client = forms.ModelChoiceField(queryset=queryset, label="Select Client")

    
class WithdrawalForm(forms.ModelForm):
    YEAR = Year.current_year()

    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=YEAR), required=False)
    class Meta:
        model = SavingsPayment
        fields = ['savings', 'amount', 'payment_date', 'transaction_type', 'description', 'bank']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'savings': Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(WithdrawalForm, self).__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            is_admin = self.user.groups.filter(name='Admin').exists()
            if not is_admin:
                self.fields['bank'].queryset = get_user_and_office_banks(self.user)
        self.fields['transaction_type'].initial = 'W'
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super(WithdrawalForm, self).save(commit=False)
        instance.client = instance.savings.client
        instance.transaction_type = SavingsPayment.WITHDRAWAL
        instance.balance = 0
        instance.amount = -instance.amount
        instance.approved = False
        if commit:
            instance.save()
        return instance


class SavingsForm(forms.ModelForm):

    YEAR = Year.current_year()
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=YEAR), required=False)
    
    class Meta:
        model = SavingsPayment
        fields = [ 'savings','amount', 'payment_date', 'bank']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'savings': Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        print(self.user)

        super(SavingsForm, self).__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            is_admin = self.user.groups.filter(name='Admin').exists()
            if not is_admin:
                self.fields['bank'].queryset = get_user_and_office_banks(self.user)

    def save(self, commit: bool = True) -> Any:
        instance = super(SavingsForm, self).save(commit=False)
        instance.client = instance.savings.client
        instance.transaction_type = SavingsPayment.SAVINGS
        instance.balance = instance.savings.balance + instance.amount
        if commit:
            instance.save()
        return super().save(commit)


class CombinedPaymentForm(forms.ModelForm):

    YEAR = Year.current_year()
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=YEAR), required=False)
    payment_schedule = forms.ModelChoiceField(queryset=PaymentSchedule.objects.none(), required=False)
    amount = forms.DecimalField(required=False)

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )

    class Meta:
        model = LoanPayment
        fields = ['client', 'payment_schedule', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'client': Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            is_admin = self.user.groups.filter(name='Admin').exists()
            if not is_admin:
                self.fields['bank'].queryset = get_user_and_office_banks(self.user)
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                loans = Loan.objects.filter(client=client_id)
                savings = Savings.objects.filter(client=client_id).exclude(type=Savings.DC).first()
                self.fields['payment_schedule'].queryset = PaymentSchedule.objects.filter(loan__in=loans).order_by('due_date')
                self.instance.savings = savings
                
            except (ValueError, TypeError, Loan.DoesNotExist):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['payment_schedule'].queryset = self.instance.loan.client.paymentschedule_set.order_by('due_date')

    def save(self, commit=True):
        loan_payment_instance = super().save(commit=False)
        savings_payment_instance = SavingsPayment()
        loan_payment_instance.loan = loan_payment_instance.payment_schedule.loan

        # Handle loan payment
        if self.cleaned_data['payment_date']:
            tran = Transaction(description=f'Combined payment from {loan_payment_instance.loan.client.name}')
            tran.save(prefix='COM')
            loan_payment_instance.transaction = tran
            loan_payment_instance.payment_date = self.cleaned_data['payment_date']
            loan_payment_instance.client = loan_payment_instance.loan.client
            loan_payment_instance.payment_schedule = self.cleaned_data['payment_schedule']
            loan_payment_instance.amount = loan_payment_instance.payment_schedule.amount_due
            loan_payment_instance.payment_schedule.is_paid = True
            loan_payment_instance.payment_schedule.payment_date = loan_payment_instance.payment_date
            loan_payment_instance.description = self.cleaned_data['description'] + f' for {loan_payment_instance.client.name}'
            loan_payment_instance.payment_schedule.save()
            if self.user:
                loan_payment_instance.created_by = self.user
            if commit:
                loan_payment_instance.save()

        # Handle savings payment
        if self.cleaned_data['payment_date']:
            
            savings_payment_instance.transaction = tran
            savings_payment_instance.client = self.cleaned_data['client']
            savings_payment_instance.amount = self.cleaned_data['amount']-loan_payment_instance.amount
            savings_payment_instance.payment_date = self.cleaned_data['payment_date']
            savings_payment_instance.savings = self.instance.savings
            if self.user:
                savings_payment_instance.created_by = self.user
            savings_payment_instance.transaction_type = SavingsPayment.SAVINGS
            if commit:
                savings_payment_instance.save()

        return loan_payment_instance, savings_payment_instance
    

from django.forms import modelformset_factory

class GroupCombinedPaymentForm(forms.Form):
    group = forms.ModelChoiceField(queryset=ClientGroup.objects.all(), label="Select Group")
    payment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Payment Date")
    bank = forms.ModelChoiceField(queryset=Bank.objects.filter(year=Year.current_year()), required=False, label="Bank")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter the bank queryset
        if self.user:
            is_admin = self.user.groups.filter(name='Admin').exists()
            if not is_admin:
                self.fields['bank'].queryset = get_user_and_office_banks(self.user)
        self.clients = []

    def populate_clients(self, group):
        self.clients = group.client_set.all()  # Assuming `clients` is a related field in `ClientGroup`
        for client in self.clients:
            self.fields[f'client_{client.id}_amount'] = forms.DecimalField(
                required=False,
                label=f"Amount Paid by {client.name}",
                min_value=0
            )
    
class ClientContributionForm(forms.ModelForm):
    class Meta:
        model = ClientContribution
        fields = ['client', 'amount']
        widgets = {
            'client': Select2Widget,
        }
    
    def save(self, commit=True):
        instance = super(ClientContributionForm, self).save(commit=False)
        # Create a Savings record for the client
        if not Savings.objects.filter(client=instance.client,type=Savings.DC).exists():
            savings = Savings.objects.create(
                client=instance.client,
                balance=0,
                type=Savings.DC
            )
            savings.save()
        if commit:
            instance.save()

class SetupMonthlyContributionsForm(forms.Form):
    client_contribution = forms.ModelChoiceField(queryset=ClientContribution.objects.all())
    month = forms.IntegerField(min_value=1, max_value=12)
    year = forms.IntegerField(min_value=1900, max_value=2100)

    def setup_monthly_contributions(self, user):
        setup_monthly_contributions(self.cleaned_data['client_contribution'], self.cleaned_data['month'], self.cleaned_data['year'], user)
        return True
class ToggleDailyContributionForm(forms.Form):
    client_contribution = forms.ModelChoiceField(queryset=ClientContribution.objects.all(), widget=Select2Widget)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    payment_made = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def save(self, request, commit=True):
        instance = self.instance
        try:
            instance = DailyContribution.objects.get(
                client_contribution=self.cleaned_data['client_contribution'],
                date=self.cleaned_data['date']
            )
            instance.payment_made = self.cleaned_data['payment_made']
        except DailyContribution.DoesNotExist:
            today = timezone.now()
            if self.cleaned_data['date'].month == today.month:
                instance = DailyContribution.objects.create(
                    client_contribution=self.cleaned_data['client_contribution'],
                    date=self.cleaned_data['date'],
                    payment_made=self.cleaned_data['payment_made']
                )
        if instance.payment_made:
            create_dc_payment(instance, request)
        else:
            raise ValueError('Payment has already been made for the selected client and date.')

        if commit:
            instance.save()

        return instance
    
class MultiDayContributionForm(forms.Form):
    client_contribution = forms.ModelChoiceField(queryset=ClientContribution.objects.all(), widget=Select2Widget)
    days = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = datetime.date.today()
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]
        choices = [
            (
                datetime.date(year, month, day).strftime('%Y-%m-%d'),
                datetime.date(year, month, day).strftime('%Y-%m-%d')
            )
            for day in range(1, days_in_month + 1)
        ]
        self.fields['days'].choices = choices

    def save(self, request, commit=True):
        client_contribution = self.cleaned_data['client_contribution']
        payment_made = True
        days = self.cleaned_data['days']
        with transaction.atomic():
            for day in days:
                date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
                
                daily_contribution, created = DailyContribution.objects.get_or_create(
                    client_contribution=client_contribution,
                    date=date
                )
                daily_contribution.payment_made = payment_made
                daily_contribution.save()
                if payment_made:
                    create_dc_payment(daily_contribution, request)
            verify_trial_balance()
        return True

class DailyContributionSpreadsheetForm(forms.Form):
    month = forms.IntegerField(min_value=1, max_value=12, initial=datetime.date.today().month, label='Month')
    year = forms.IntegerField(min_value=2000, max_value=datetime.date.today().year, initial=datetime.date.today().year, label='Year')
    contributions = forms.CharField(widget=forms.HiddenInput(), required=False)

class MonthYearForm(forms.Form):
    month = forms.IntegerField(min_value=1, max_value=12, initial=datetime.date.today().month, label='Month')
    year = forms.IntegerField(min_value=2000, max_value=datetime.date.today().year, initial=datetime.date.today().year, label='Year')