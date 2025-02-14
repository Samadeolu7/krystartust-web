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
from savings.models import ClientContribution, DailyContribution, Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Find all reversed loan payment with reference number COM-54040012025 and see its details'

    def handle(self, *args, **kwargs):

        loan_payment = LoanPayment.objects.filter(transaction__reference_number='COM-54040012025').first()
        if loan_payment:
            self.stdout.write(self.style.SUCCESS(f'Loan Payment found with reference number {loan_payment.transaction.reference_number}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment amount {loan_payment.amount}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment date {loan_payment.payment_date}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment client {loan_payment.client.name}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment loan {loan_payment.loan.client.name}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment schedule {loan_payment.payment_schedule}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment is paid {loan_payment.payment_schedule.is_paid}'))
            self.stdout.write(self.style.SUCCESS(f'Loan Payment schedule payment amount {loan_payment.payment_schedule.amount_due}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'No Loan Payment found with reference number COM-54040012025'))
            
        
                