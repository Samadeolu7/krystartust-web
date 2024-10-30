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
        # find all income from loan interest and reduce payment datein the last 2 weeks by 2 weeks 
        today = timezone.now()
        two_weeks_ago = today - timezone.timedelta(weeks=2)
        income = IncomePayment.objects.filter(income__name='Weekly Loan Interest', payment_date__gte=two_weeks_ago)
        for i in income:
            i.payment_date = i.payment_date - timezone.timedelta(weeks=4)
            i.save()
            self.stdout.write(self.style.SUCCESS(f'Updated {i}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated loan interest payments'))