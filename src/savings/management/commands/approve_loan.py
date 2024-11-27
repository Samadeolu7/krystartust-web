from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import timedelta
from income.models import IncomePayment
from loan.models import Loan, LoanRepaymentSchedule
from administration.models import Transaction
from main.utils import verify_trial_balance

class Command(BaseCommand):
    help = 'Find monthly loan where the interest income is on a diffrent payment date than loan start date'

    def handle(self, *args, **kwargs):
        loans = Loan.objects.filter(loan_type='Monthly').all()
        for loan in loans:
            #find interest income payment with the same transaction model as loan
            if loan.transaction:
                interest_income_payment = IncomePayment.objects.filter(transaction=loan.transaction).first()
            #find interest income payment with the same creation date as the loan
                if not interest_income_payment:
                    interest_income_payment = IncomePayment.objects.filter(created_at=loan.created_at).first()
                    interest_income_payment.transaction = loan.transaction
                    interest_income_payment.save()
              
            else:
                interest_income_payment = IncomePayment.objects.filter(created_at=loan.created_at).first()
            print(f'Loan: {loan.start_date} - Interest Income Payment: {interest_income_payment.payment_date}')
        