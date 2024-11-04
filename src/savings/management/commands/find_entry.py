# management/commands/find_entry.py

from django.core.management.base import BaseCommand
from decimal import Decimal
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from loan.models import LoanPayment, Loan
from bank.models import BankPayment
from savings.models import SavingsPayment, Savings
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from django.db.models import Q
from datetime import timedelta
import csv
import os

import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.apps import apps

class Command(BaseCommand):
    help = 'Find any entry of 300 in the last 4 days'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
        four_days_ago = today - timedelta(days=4)
        start_of_four_days_ago = timezone.make_aware(timezone.datetime.combine(four_days_ago, timezone.datetime.min.time()))
        # Get all the models from the installed apps
        models = apps.get_models()
        # Loop through all the models
        for model in models:
            # Check if the model has a field named 'amount'
            if hasattr(model, 'amount'):
                # Check if the model has a field named 'created_at'
                if hasattr(model, 'created_at'):
                    # Get all the objects created in the last 4 days
                    entries = model.objects.filter(created_at__gte=start_of_four_days_ago, created_at__lte=end_of_day)
                    # Loop through all the entries
                    for entry in entries:
                        # Check if the amount is 300
                        if hasattr(entry, 'amount'):
                            if entry.amount == Decimal('300'):
                                print(f'Found an entry of 300 in {model.__name__} with id {entry.id}')

        

                    