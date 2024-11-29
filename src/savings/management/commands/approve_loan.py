from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from income.models import IncomePayment
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from administration.models import Transaction
from main.utils import verify_trial_balance
from django.utils import timezone

class Command(BaseCommand):
    help = 'Find all monthly loans and recalculate the date in due date using months from start date'

    def handle(self, *args, **kwargs):
        loans = Loan.objects.filter(loan_type='Monthly')

        for loan in loans:
            # Get the number of months between the start date and the end date
            months = loan.duration
            # Get the end date of the loan
            loan_payments = LoanPayment.objects.filter(loan=loan)
            for payment in loan_payments:
                payment.payment_schedule = LoanRepaymentSchedule.objects.filter(loan=loan, is_paid=False).first()
                payment.payment_schedule.is_paid = True
                payment.payment_schedule.payment_date = payment.payment_date
                payment.payment_schedule.save()
                payment.save()
            
            self.stdout.write(self.style.SUCCESS('Successfully updated loan repayment schedule'))
        self.stdout.write(self.style.SUCCESS('Successfully updated all loan repayment schedule'))