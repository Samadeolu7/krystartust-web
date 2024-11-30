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
    help = 'Find all bank with transaction.reference_number starting with COM and if there are any payments with the same reference number, combine them into one payment'

    def handle(self, *args, **kwargs):
        # Get all the bank payments with reference number starting with COM
        bank_payments = BankPayment.objects.filter(transaction__reference_number__startswith='COM').order_by('transaction__reference_number')
        # Find transactions with the same reference number
        for payment in bank_payments:
            payments = BankPayment.objects.filter(transaction__reference_number=payment.transaction.reference_number)
            if payments.count() > 1:
                with transaction.atomic():
                    # Combine the payments
                    total_amount = Decimal('0.00')
                    for p in payments:
                        total_amount += p.amount
                    # Get the first payment
                    first_payment = payments.first()
                    # Update the first payment with the total amount
                    first_payment.amount = total_amount
                    first_payment.save()
                    # Delete the other payments
                    payments.exclude(pk=first_payment.pk).delete()

                self.stdout.write(self.style.SUCCESS(f'Combined payments for reference number {payment.transaction.reference_number} with {payments.count()} payments'))
                