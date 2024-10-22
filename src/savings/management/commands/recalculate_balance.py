from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

import pytz
from loan.models import LoanRepaymentSchedule, Loan
from django.db import transaction

class Command(BaseCommand):
    help = 'Shift the due date of all LoanRepaymentSchedule entries created before 10-10-2024 by one week'

    def handle(self, *args, **kwargs):
        # find all loans and set the approved to true
        loans = Loan.objects.filter(approved=False)
        for loan in loans:
            loan.approved = True
            loan.save()
            print(f"Loan {loan.id} approved.")
        self.stdout.write(self.style.SUCCESS('Successfully approved all loans'))