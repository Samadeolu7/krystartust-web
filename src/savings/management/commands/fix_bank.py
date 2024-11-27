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
    help = 'Find all loans where the emi is not equal to the amount_due in the repayment schedule'

    def handle(self, *args, **kwargs):
        # Get all the loans
        loans = Loan.objects.all()
        for loan in loans:
            emi = loan.emi
            # Get the amount due from any of the repayment schedule
            amount_due = loan.repayment_schedule.first()
            # Check if the emi is not equal to the amount due
            if amount_due:
                amount_due = amount_due.amount_due
            else:
                print(f'Loan: {loan.client.name} - No repayment schedule found')
                continue
            if emi != amount_due:
                print(f'Loan: {loan.client.name} - EMI: {emi} - Amount Due: {amount_due}')
                # Update the emi to be equal to the amount due
                loan.emi = amount_due
                loan.save()
                print(f'Loan: {loan.client.name} - EMI updated to {amount_due}')
                