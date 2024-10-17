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
        #for all loans find their loan payments and ensure that the corresponding loan repayment schedule is marked as paid

        #get all loans
        loans = Loan.objects.all()
        for loan in loans:
            #get all loan payments for the loan
            loan_payments = LoanPayment.objects.filter(loan=loan)
            for loan_payment in loan_payments:
                #get the loan repayment schedule for the payment
                loan_repayment_schedule = loan.repayment_schedule.filter(due_date=loan_payment.payment_date).first()
                if loan_repayment_schedule:
                    if loan_repayment_schedule.is_paid == True:
                        loan_repayment_schedule.payment_date = loan_payment.payment_date
                        loan_repayment_schedule.save()

        #success message
        self.stdout.write(self.style.SUCCESS('Successfully found entries'))

                    