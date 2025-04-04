from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from administration.models import Transaction
from bank.models import Bank, BankPayment
from client.models import Client
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from main.utils import verify_trial_balance
from savings.models import ClientContribution, DailyContribution, Savings, SavingsPayment
from liability.models import Liability, LiabilityPayment
from django.db import transaction
from django.db.models import Q

from income.utils import create_loan_registration_fee_income_payment
from income.models import RegistrationFee

class Command(BaseCommand):
    help = 'Ensure loan repayments are applied chronologically'

    def handle(self, *args, **kwargs):
        # Find all loans
        client = Client.objects.get(name='Modupe Mosunmola Oladokun')
        loans = Loan.objects.filter(client=client)
        with transaction.atomic():
            for loan in loans:
                # Get repayment schedules ordered by due_date
                repayment_schedules = LoanRepaymentSchedule.objects.filter(
                    loan=loan
                ).order_by('due_date')

                # Track the last unpaid schedule
                last_unpaid_schedule = None
                schedule= None
                for schedule in repayment_schedules:
                    schedule.is_paid = True
                    schedule.save()
                    # if not schedule.is_paid:
                    #     last_unpaid_schedule = schedule
                    # elif last_unpaid_schedule:
                    #     # If we find a paid schedule after an unpaid one, adjust the status
                    #     last_unpaid_schedule_id = last_unpaid_schedule.id
                    #     schedule.is_paid = False
                    #     schedule.save(update_fields=['is_paid'])
                    #     last_unpaid_schedule.is_paid = True
                    #     last_unpaid_schedule.save(update_fields=['is_paid'])
                    #     last_unpaid_schedule = None
                if schedule:
                    schedule.is_paid=False
                    schedule.payment_date = None
                    schedule.save()
                    print(f'Adjusted LoanRepaymentSchedule for loan {loan.id}: {schedule.id} -> unpaid, -> paid')
        print('Completed adjusting loan repayment schedules')