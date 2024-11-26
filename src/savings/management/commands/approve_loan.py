from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import timedelta
from loan.models import Loan, LoanRepaymentSchedule
from administration.models import Transaction
from main.utils import verify_trial_balance

class Command(BaseCommand):
    help = 'Combine multiple active loans for clients into a single loan'

    def handle(self, *args, **kwargs):
        clients = Loan.objects.values_list('client', flat=True).distinct()
        for client_id in clients:
            active_loans = Loan.objects.filter(client_id=client_id, status='Active')
            if active_loans.count() > 1:
                self.combine_loans(client_id, active_loans)

    def combine_loans(self, client_id, active_loans):
        try:
            with transaction.atomic():
                latest_loan = active_loans.order_by('-start_date').first()
                total_balance = sum(loan.balance for loan in active_loans)
                
                # Create a new combined loan
                latest_loan.balance = total_balance
                latest_loan.save()

                active_loans = active_loans.exclude(id=latest_loan.id)
                # Set old loans to inactive and delete their repayment schedules
                for loan in active_loans:
                    loan.status = 'Inactive'
                    loan.balance = 0
                    loan.save()
                    LoanRepaymentSchedule.objects.filter(loan=loan).delete()
                LoanRepaymentSchedule.objects.filter(loan=latest_loan).delete()
                # Create new repayment schedule for the combined loan
                time_increment = {
                    'Daily': timedelta(days=1),
                    'Weekly': timedelta(weeks=1),
                    'Monthly': timedelta(weeks=4),
                }.get(latest_loan.loan_type)
                start_date = latest_loan.start_date
                if time_increment == timedelta(weeks=4):
                    start_date = start_date + timedelta(weeks=5)
                if time_increment == timedelta(weeks=1):
                    start_date = start_date + timedelta(weeks=2)
                if time_increment == timedelta(days=1):
                    start_date = start_date + timedelta(days=1)
                amount_due = latest_loan.balance / latest_loan.duration
                for i in range(int(latest_loan.duration)):
                    due_date = start_date + (i * time_increment)
                    LoanRepaymentSchedule.objects.create(
                        loan=latest_loan,
                        due_date=due_date,
                        amount_due=amount_due,
                    )

                verify_trial_balance()
                self.stdout.write(self.style.SUCCESS(f'Successfully combined loans for client {client_id}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error combining loans for client {client_id}: {e}'))