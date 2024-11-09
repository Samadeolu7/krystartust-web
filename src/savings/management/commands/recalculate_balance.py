from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

import pytz
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from loan.models import LoanRepaymentSchedule, Loan, LoanPayment
from administration.models import Transaction
from bank.models import Bank, BankPayment
from django.db import transaction
from django.db.models import Sum

from savings.models import Savings, SavingsPayment, DailyContribution

class Command(BaseCommand):
    help = 'Find all Daily Contribution transactions'

    def handle(self, *args, **kwargs):
        # find all the SavingsPayment records with transaction type Daily Contribution
        dc_payments = SavingsPayment.objects.filter(transaction_type=SavingsPayment.DC)
        for dc_payment in dc_payments:
            print(f'Found a Daily Contribution payment {dc_payment.id} for {dc_payment.client.name} of {dc_payment.amount} on {dc_payment.payment_date}')
        print(f'Total number of Daily Contribution payments found: {dc_payments.count()}')
        # find all the Savings records with type Daily Contribution
        dc_savings = Savings.objects.filter(type=Savings.DC)
        for dc_saving in dc_savings:
            print(f'Found a Daily Contribution savings record for {dc_saving.client.name} with a balance of {dc_saving.balance}')
        print(f'Total number of Daily Contribution savings records found: {dc_savings.count()}')
        # find all the Daily Contribution records
        daily_contributions = DailyContribution.objects.all()
        for dc in daily_contributions:
            if dc.payment_made:
                print(f'Found a Daily Contribution record for {dc.client_contribution.client.name} for {dc.date} of {dc.client_contribution.amount}')