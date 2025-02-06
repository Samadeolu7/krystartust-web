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
    help = 'Find all DC savings payments created in the last 24 hours and add them to csv'

    def handle(self, *args, **kwargs):
        # Get all savings payments created in the last 24 hours
        now = timezone.now()
        start = now - timezone.timedelta(days=1)
        end = now
        savings_payments = SavingsPayment.objects.filter(created_at__range=(start, end), transaction_type='C')
        if not savings_payments:
            print('No DC payments found')
            return
        # Create csv file
        file_name = 'dc_payments.csv'
        with open(file_name, 'w') as file:
            file.write('Client,Amount,Date,Payment Date,Created At\n')
            for payment in savings_payments:
                file.write(f'{payment.client},{payment.amount},{payment.payment_date},{payment.created_at}\n')
        print('DC payments added to csv')
        
                
