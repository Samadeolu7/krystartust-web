# management/commands/find_entry.py

from django.core.management.base import BaseCommand
from decimal import Decimal
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from loan.models import LoanPayment, Loan
from bank.models import BankPayment
from savings.models import SavingsPayment, Savings
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from django.db.models import Q
from datetime import timedelta
import csv
import os

class Command(BaseCommand):
    help = 'Find all loans where the loan start date is less than four weeks from the first repayment date'

    def handle(self, *args, **kwargs):
        # find all loans where the loan start date is less than two weeks from the first repayment date
        loans = Loan.objects.filter(loan_type='Monthly').all()
        loans_lst = []
        for loan in loans:
            if loan.start_date + timedelta(weeks=4) -timedelta(days=1) >= loan.repayment_schedule.first().due_date:
                self.stdout.write(self.style.SUCCESS(f'Loan {loan.id} has a start date less than four weeks from the first repayment date'))
                # reduce the start date by 2 weeks
                loan.start_date = loan.start_date - timedelta(days=14)
                loan.save()
                loans_lst.append(loan)
        # write the loans to a csv file
        with open('loans.csv', mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(['Loan ID', 'Client ID', 'Start Date', 'First Repayment Date'])
            for loan in loans_lst:
                writer.writerow([loan.id, loan.client.id, loan.start_date, loan.repayment_schedule.first().due_date])

        # success message
        self.stdout.write(self.style.SUCCESS('Transactions written to transactions.csv'))

                    