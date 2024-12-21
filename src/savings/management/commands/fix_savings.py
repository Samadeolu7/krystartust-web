# management/commands/fix_payments.py

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan
from main.utils import verify_trial_balance
from savings.models import Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Make all income payment for a savings of type DC carry the same decription as their corresponding transaction description'

    def handle(self, *args, **kwargs):
        # Get all income payments for savings of type DC
        income_payments = IncomePayment.objects.filter(transaction__reference_number__startswith='DC')
        for income_payment in income_payments:
            with transaction.atomic():
                income_payment.description = income_payment.transaction.description
                income_payment.save()
                print(f'Updated {income_payment} description to {income_payment.transaction.description}')
                
