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
    help = 'Compare the savings payments of each client to their savings balance'

    def handle(self, *args, **kwargs):
        # Get all the savings
        savings = Savings.objects.all().order_by('id')
        faulty_savings = []
        for saving in savings:
            # Get all the savings payments
            payments = SavingsPayment.objects.filter(savings=saving).order_by('payment_date')
            balance = 0
            for payment in payments:
                balance += payment.amount
            if balance < saving.balance:
                print(f'{saving.client} has a negative balance of {saving.balance - balance} on {payment.payment_date}')
                faulty_savings.append(saving)
            elif balance == saving.balance:
                print(f'{saving.client} has a zero balance on {payment.payment_date}')
            else:
                print(f'{saving.client} has a positive balance of {saving.balance - balance} on {payment.payment_date}')
                faulty_savings.append(saving)

        # write the faulty savings to a file
        with open('faulty_savings.txt', 'w') as file:
            for saving in faulty_savings:
                file.write(f'{saving.client} has a faulty savings account\n')
        print('Faulty savings written to faulty_savings.txt')
        print('Done')


            