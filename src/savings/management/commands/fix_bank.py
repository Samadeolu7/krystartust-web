# management/commands/fix_payments.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from savings.models import Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Fix payments that did not hit the bank'

    def handle(self, *args, **kwargs):
        # Define the payments that need to be fixed
#print all transaction with oct 11 2024 as their created at date
        bankpayments=[]
        expenses=[]
        incomes=[]
        savings=[]
        liabilities=[]

        payments = BankPayment.objects.filter(created_at__date=datetime(2024, 10, 11))
        for payment in payments:
            bankpayments.append(payment)
        payments = ExpensePayment.objects.filter(created_at__date=datetime(2024, 10, 11))
        for payment in payments:
            expenses.append(payment)
        payments = IncomePayment.objects.filter(created_at__date=datetime(2024, 10, 11))
        for payment in payments:
            incomes.append(payment)
        payments = SavingsPayment.objects.filter(created_at__date=datetime(2024, 10, 11))
        for payment in payments:
            savings.append(payment)
        payments = LiabilityPayment.objects.filter(created_at__date=datetime(2024, 10, 11))
        for payment in payments:
            liabilities.append(payment)

        all = bankpayments + expenses + incomes + savings + liabilities

        #bring payments that happened almost at the same time together and print therm under the time
        all.sort(key=lambda x: x.created_at)
        for payment in all:
            print(payment.created_at, payment)
        # Fix the payments
