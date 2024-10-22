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
from django.db.models import Q
from datetime import timedelta
import csv
import os

class Command(BaseCommand):
    help = 'Find entries within the specified dates and write to CSV'

    def handle(self, *args, **kwargs):
        # find all transactions that happened in the past 3 days
        start_date = timezone.now() - timedelta(days=3)
        end_date = timezone.now()
        transactions = []
        transactions.append(['Transaction Date', 'Transaction Type', 'Description', 'Amount', 'Bank'])
        # get all loan payments
        loan_payments = LoanPayment.objects.filter(payment_date__range=[start_date, end_date])
        for payment in loan_payments:
            transactions.append([payment.payment_date, 'Loan Payment', payment.client, payment.amount, payment.payment_date])
        # get all bank payments
        bank_payments = BankPayment.objects.filter(payment_date__range=[start_date, end_date])
        for payment in bank_payments:
            transactions.append([payment.payment_date, 'Bank Payment', payment.description, payment.amount, payment.bank])
        # get all savings payments
        savings_payments = SavingsPayment.objects.filter(payment_date__range=[start_date, end_date])
        for payment in savings_payments:
            transactions.append([payment.payment_date, 'Savings Payment', payment.description, payment.amount, payment.bank])
        # get all expenses
        expenses = ExpensePayment.objects.filter(expense_date__range=[start_date, end_date])
        for expense in expenses:
            transactions.append([expense.payment_date, 'Expense', expense.description, expense.amount, expense.payment_date])
        # get all incomes
        incomes = IncomePayment.objects.filter(income_date__range=[start_date, end_date])
        for income in incomes:
            transactions.append([income.payment_date, 'Income', income.description, income.amount, income.payment_date])
        # sort transactions by date
        transactions[1:] = sorted(transactions[1:], key=lambda x: x[0])
        # write to CSV
        with open('transactions.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(transactions)

        # success message
        self.stdout.write(self.style.SUCCESS('Transactions written to transactions.csv'))

                    