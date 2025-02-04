# management/commands/fix_payments.py

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from administration.models import Transaction
from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan, LoanPayment
from main.utils import verify_trial_balance
from savings.models import ClientContribution, DailyContribution, Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Find all daily contributions that have does not have a corresponding income payment'

    def handle(self, *args, **kwargs):
        # Get all the loan payments
        client = ClientContribution.objects.all()
        for contribution in client:
            # Get the income payment for the loan payment
            income = Income.objects.get(name='Client Contribution')
            income_payment = IncomePayment.objects.filter(income=income, payment_date=contribution.payment_date, amount=contribution.amount).first()
            if not income_payment:
                print(f'No income payment for {contribution.client} on {contribution.payment_date} of {contribution.amount}')
                # Create the income payment
        #         income = Income.objects.get(name='Client Contribution')
        #         income_payment = IncomePayment(client=contribution.client, income=income, amount=contribution.amount, payment_date=contribution.payment_date)
        #         income_payment.save()
        #         print(f'Income payment created for {contribution.client} on {contribution.payment_date} of {contribution.amount}')
        # #
        
                