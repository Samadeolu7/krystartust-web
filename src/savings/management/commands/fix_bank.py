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
    help = 'Find all loans of type monthly and add 3 weeks to the due dates of their repayment schedules'

    def handle(self, *args, **kwargs):
        loan = Loan.objects.filter(loan_type='Monthly')
        for l in loan:
            for s in l.repayment_schedule.all():
                s.due_date = s.due_date + timezone.timedelta(weeks=2)
                s.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated due dates of monthly loans repayment schedules'))