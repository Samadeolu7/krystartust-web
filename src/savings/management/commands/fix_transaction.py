# management/commands/fix_payments.py

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from administration.models import Transaction
from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan, LoanPayment
from main.utils import verify_trial_balance
from savings.models import Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Find all loan payments with a transaction reference number that starts with "COM"'

    def handle(self, *args, **kwargs):
        # Get all the loan payments
        trans = Transaction.objects.filter(reference_number__startswith='COM')
        loan_payments = LoanPayment.objects.filter(transaction__in=trans)
        for loan_payment in loan_payments:

            if loan_payment.amount!=loan_payment.loan.emi:
                with transaction.atomic():
                    print(f'Loan Payment: {loan_payment.client.name} - {loan_payment.amount} - {loan_payment.payment_date} - {loan_payment.loan.emi} ')
                    tran = loan_payment.transaction
                    savings = SavingsPayment.objects.filter(transaction=tran).first()
                    #take out the balance for the emi fron the savings account
                    balance = loan_payment.loan.emi - loan_payment.amount
                    savings.amount -= balance
                    savings.save()
                    loan_payment.amount = loan_payment.loan.emi
                    loan_payment.save()
                    savings.savings.balance -= balance
                    savings.savings.save()
                    loan_payment.loan.balance -= balance
                    loan_payment.loan.save()
                    verify_trial_balance()
                    print(f'Loan Payment: {loan_payment.client.name} - {loan_payment.amount} - {loan_payment.payment_date} - {loan_payment.loan.emi} ')
                    print('fixing done')
        print('Done')
        
                