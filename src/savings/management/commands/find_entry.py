# management/commands/find_entry.py

from django.core.management.base import BaseCommand
from decimal import Decimal
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from loan.models import LoanPayment, Loan
from datetime import timedelta
import csv
import os

class Command(BaseCommand):
    help = 'Find entries within the specified dates and write to CSV'

    def handle(self, *args, **kwargs):
        
        loan_payments = LoanPayment.objects.all()
        for loan_payment in loan_payments:
            #get the loan repayment schedule for the payment
            loan_repayment_schedule = loan_payment.payment_schedule
            if loan_repayment_schedule:
                if loan_repayment_schedule.is_paid == True:
                    pass
                else:
                    print(f'Loan repayment schedule for {loan_payment.client.name} on {loan_payment.payment_date} is not marked as paid')
                    loan_repayment_schedule.is_paid = True
                    loan_repayment_schedule.payment_date = loan_payment.payment_date
                    loan_repayment_schedule.save()

        #success message
        self.stdout.write(self.style.SUCCESS('Successfully found entries'))

                    