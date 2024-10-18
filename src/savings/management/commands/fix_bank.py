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
    help = 'Fix payments that did not hit the bank'

    def handle(self, *args, **kwargs):
        # Calculate 15% of the total loan amount
        # Find all income payments and liability that are ahead of today in date
        # Find all loan payments that are ahead of today in date

        for bank in Bank.objects.all():
            bank_payments = BankPayment.objects.filter(bank=bank, payment_date__gt=timezone.now())
            # Reduce the date of such payments by 14 days
            for payment in bank_payments:
                payment.payment_date = payment.payment_date - timezone.timedelta(days=14)
                payment.save()
                print(f"Fixed bank payment for {bank.name}")
                
        for income in Income.objects.all():
            income_payments = IncomePayment.objects.filter(income=income, payment_date__gt=timezone.now())
            if not income_payments.exists():
                print(f"No future income payments found for {income.name}")
            for payment in income_payments:
                try:
                    print(f"Original payment date for {income.name}: {payment.payment_date}")
                    payment.payment_date = payment.payment_date - timezone.timedelta(days=14)
                    payment.save()
                    print(f"Fixed income payment for {income.name}")
                except Exception as e:
                    print(f"Error fixing income payment for {income.name}: {e}")
        
        for liability in Liability.objects.all():
            liability_payments = LiabilityPayment.objects.filter(liability=liability, payment_date__gt=timezone.now())
            for payment in liability_payments:
                payment.payment_date = payment.payment_date - timezone.timedelta(days=14)
                payment.save()
                print(f"Fixed liability payment for {liability.name}")

        # Success message
        self.stdout.write(self.style.SUCCESS('Successfully fixed payments'))