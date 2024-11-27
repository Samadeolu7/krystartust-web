from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import timedelta
from income.models import IncomePayment
from loan.models import Loan, LoanRepaymentSchedule
from administration.models import Transaction
from main.utils import verify_trial_balance
from django.utils import timezone

class Command(BaseCommand):
    help = 'Find monthly loan where the interest income is on a diffrent payment date than loan start date'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        loans = Loan.objects.all()

        for loan in loans:
            #find interest income payment with the same transaction model as loan
            print(f'Loan: {loan.client.name} - {loan.start_date}')
            if loan.transaction:
                interest_income_payment = IncomePayment.objects.filter(transaction=loan.transaction).first()
            #find interest income payment with the same creation date as the loan
                if not interest_income_payment:
                    #look for interest income payment with the same creation date as the loan
                    interest_income_payment = IncomePayment.objects.filter(created_at=loan.created_at).first()
                    interest_income_payment.transaction = loan.transaction
                    interest_income_payment.save()

            elif loan.transaction == None:
                interest_income_payment = IncomePayment.objects.filter(created_at=loan.created_at).first()
                if interest_income_payment:
                    interest_income_payment.transaction = loan.transaction
                    interest_income_payment.save()
                else:
                    name = loan.client.name
                    #find an interest income with the client name in its description
                    interest_income_payment = IncomePayment.objects.filter(description__contains=name)
                    if interest_income_payment:
                        interest_income_payment=interest_income_payment.first()
                        interest_income_payment.transaction = loan.transaction
                        interest_income_payment.save()
                    else:
                        print(f'No interest income payment found for {loan.client.name}')
                        continue

            if loan.start_date != interest_income_payment.payment_date:    
                print(f'Loan: {loan.start_date} - Interest Income Payment: {interest_income_payment.payment_date}')
                interest_income_payment.payment_date = loan.start_date
                interest_income_payment.save()
                print(f'Interest income payment date updated to {loan.start_date}')
        