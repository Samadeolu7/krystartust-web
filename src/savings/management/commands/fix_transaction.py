from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from administration.models import Transaction
from bank.models import Bank, BankPayment, recalculate_balance_after_payment_date
from client.models import Client
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from main.utils import verify_trial_balance
from savings.models import ClientContribution, DailyContribution, Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction
from django.db.models import Q

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Recalculate balance for all banks starting from jan 1 2025'


    def handle(self, *args, **options):

        # Get all banks
        banks = Bank.objects.all()

        for bank in banks:
            recalculate_balance_after_payment_date(bank.id, datetime(2025,1,1))
            print(f"Recalculated balance for bank {bank.name} starting from 2025-01-01")