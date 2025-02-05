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
    help = 'Find all reversed loan payment and reset the repayment schedule'

    def handle(self, *args, **kwargs):
        # Get all the loan payments that have been reversed
        reversed_loan_payments = LoanPayment.objects.filter(transaction__reference_number__startswith='REV').all()
        for payment in reversed_loan_payments:
            print(f'Processing {payment.client.name}')
            repayment = payment.payment_schedule
            # Reset the payment schedule
            if repayment:
                repayment.is_paid = False
                repayment.payment_date = None
                repayment.save()
                print(f'Reset repayment schedule for {payment.client.name}')
            
        
                