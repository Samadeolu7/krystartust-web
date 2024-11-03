from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from loan.models import Loan
from user.models import User
from administration.models import Approval
from loan.utils import approve_loan

class Command(BaseCommand):
    help = 'Approve a loan by its approval ID'


    def handle(self, *args, **kwargs):
        loans = Loan.objects.get(id=77)
        loan_repayment = loans.repayment_schedule.first()

        print(f"loan_repayment.due_date: {loan_repayment.due_date}, loan start date: {loans.start_date}")