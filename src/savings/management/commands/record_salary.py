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
from user.models import User
from user.pdf_gen import generate_payslip
from user.scheduled import record_salary_expense

class Command(BaseCommand):
    help = 'Record salary expense for all users'

    def handle(self, *args, **kwargs):
        self.save_salary_expense()
        print('Done')
                
    def save_salary_expense(self):
        users = User.objects.all()
        for user in users:
            record_salary_expense(user)
            print(f'Salary expense recorded for {user.username}')
        return True