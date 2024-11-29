# management/commands/fix_payments.py

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan
from main.utils import verify_trial_balance
from savings.models import Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Find all withdrawals where the amount was positive and update the amount to be negative and print them'

    def handle(self, *args, **kwargs):
        # Get all the withdrawals
        savings_payments = SavingsPayment.objects.filter(transaction_type='W', amount__gt=0)
        for savings_payment in savings_payments:
            with transaction.atomic():
                print(f'Withdrawal: {savings_payment.savings.client.name} - {savings_payment.amount} - {savings_payment.savings.balance} - {savings_payment.payment_date}')
                savings_payment.amount = -savings_payment.amount
                savings_record = savings_payment.savings
                savings_record.balance += savings_payment.amount*2
                print(f'Updated Withdrawal: {savings_payment.savings.client.name} - {savings_payment.amount} - {savings_payment.savings.balance} - {savings_payment.payment_date}')
                savings_payment.balance = savings_record.balance
                #set transaction type to U for update
                savings_payment.transaction_type = "U"
                #find the bank with the same transaction as the savings payment
                bank_payment = BankPayment.objects.filter(transaction=savings_payment.transaction).first()
                bank_payment.amount = savings_payment.amount
                print(f'Banks balance before: {bank_payment.bank}')
                bank_payment.bank.balance += savings_payment.amount *2
                bank_payment.save()
                print(f'Banks balance after: {bank_payment.bank}')
                bank_payment.bank.save()
                savings_record.save()
                savings_payment.save()

                verify_trial_balance()
                print(f'Updated Withdrawal: {savings_payment.savings.client.name} - {savings_payment.amount} - {savings_payment.payment_date}')
        print('All Withdrawals have been updated')
