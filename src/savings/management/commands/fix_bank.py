# management/commands/fix_payments.py

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan
from savings.models import Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Fix payments that did not hit the bank'

    def handle(self, *args, **kwargs):
        #calculate 15% of the total loan amount
        total_loan_amount = 0
        for loan in Loan.objects.all():
            total_loan_amount += loan.amount
        result = total_loan_amount * Decimal(0.15)
        print(f"15% of the total loan amount is {result}")