from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

import pytz
from loan.models import LoanRepaymentSchedule, Loan, LoanPayment
from administration.models import Transaction
from bank.models import BankPayment
from django.db import transaction

class Command(BaseCommand):
    help = 'Shift the due date of all LoanRepaymentSchedule entries created before 10-10-2024 by one week'

    def handle(self, *args, **kwargs):
        # find all payment that has a transaction 10 as its transaction

        transaction = Transaction.objects.get(id=101)
        bank_payments = BankPayment.objects.filter(transaction=transaction)
        for payments in bank_payments:
            print(f'Processing payment {payments.id}')
            