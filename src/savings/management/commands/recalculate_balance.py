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

from savings.models import Savings, SavingsPayment

class Command(BaseCommand):
    help = 'Shift the due date of all LoanRepaymentSchedule entries created before 10-10-2024 by one week'

    def handle(self, *args, **kwargs):
        # find all transactions that happened today
        today = timezone.now().date()
        transactions = Transaction.objects.filter(created_at__date=today)
        loan_payments = LoanPayment.objects.filter(created_at__date=today)
        bank_payments = BankPayment.objects.filter(created_at__date=today)
        savings = SavingsPayment.objects.filter(created_at__date=today)
        expenses = ExpensePayment.objects.filter(created_at__date=today)
        incomes = IncomePayment.objects.filter(created_at__date=today)
        liabilities = LiabilityPayment.objects.filter(created_at__date=today)

        # group payments with the same transaction together
        grouped_payments = {}
        for payment in loan_payments:
            transaction_id = payment.transaction.id if payment.transaction else None
            if transaction_id in grouped_payments:
                grouped_payments[transaction_id].append(payment)
            else:
                grouped_payments[transaction_id] = [payment]
        for payment in bank_payments:
            transaction_id = payment.transaction.id if payment.transaction else None
            if transaction_id in grouped_payments:
                grouped_payments[transaction_id].append(payment)
            else:
                grouped_payments[transaction_id] = [payment]
        for payment in savings:
            transaction_id = payment.transaction.id if payment.transaction else None
            if transaction_id in grouped_payments:
                grouped_payments[transaction_id].append(payment)
            else:
                grouped_payments[transaction_id] = [payment]
        for payment in expenses:
            transaction_id = payment.transaction.id if payment.transaction else None
            if transaction_id in grouped_payments:
                grouped_payments[transaction_id].append(payment)
            else:
                grouped_payments[transaction_id] = [payment]
        for payment in incomes:
            transaction_id = payment.transaction.id if payment.transaction else None
            if transaction_id in grouped_payments:
                grouped_payments[transaction_id].append(payment)
            else:
                grouped_payments[transaction_id] = [payment]
        for payment in liabilities:
            transaction_id = payment.transaction.id if payment.transaction else None
            if transaction_id in grouped_payments:
                grouped_payments[transaction_id].append(payment)
            else:
                grouped_payments[transaction_id] = [payment]

        # write the group transaction to a csv file
        with open('transactions.csv', 'w') as file:
            file.write('Transaction ID,Amount,Payment Date,Transaction Type,Description\n')
            for transaction_id, payments in grouped_payments.items():
                if transaction_id is not None:
                    transaction = Transaction.objects.get(id=transaction_id)
                    file.write(f'{transaction.id},{transaction.created_at},{transaction.description}\n')
                    for payment in payments:
                        file.write(f'{transaction.id},{payment.amount},{payment.created_at}\n')
                else:
                    for payment in payments:
                        file.write(f'None,{payment.amount},{payment.created_at},Unknown,No transaction\n')
        self.stdout.write(self.style.SUCCESS('Transactions written to transactions.csv'))