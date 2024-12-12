from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from client.models import Client
from income.models import IncomePayment
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from administration.models import Transaction
from main.utils import verify_trial_balance
from django.utils import timezone

class Command(BaseCommand):
    help = 'Find all weekly loans and recalculate the date in due date using months from start date'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                clients = Client.objects.filter(client_id='WL0029').first()
                loan = Loan.objects.filter(client=clients, loan_type= Loan.WEEKLY).latest('start_date')
                loan_repayment_schedule = LoanRepaymentSchedule.objects.filter(loan=loan)
                start_date = loan.start_date
                end_date = start_date + timedelta(weeks=25)
                balance = loan.balance
                #delete all loan repayment schedule
                LoanRepaymentSchedule.objects.filter(loan=loan).delete()
                #create new ones using the current balance and ends on the end date
                time_increment = relativedelta(weeks=1)
                
                today = timezone.now().date()
                date = today - timedelta(days=2)
                duration = 11
                amount_due = balance / duration
                remainder = balance
                for i in range(duration):   
                    due_date = date + ((i) * time_increment)
                    if i == duration - 1:
                        amount_due = remainder
                    LoanRepaymentSchedule.objects.create(loan=loan, due_date=due_date, amount_due=amount_due)
                    remainder -= amount_due
                    print(remainder)
                
                verify_trial_balance()
                    
        except Exception as e:
            print(e)
            print("Done")