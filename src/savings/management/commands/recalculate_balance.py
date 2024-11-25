from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

import pytz
from django.apps import apps
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from loan.models import LoanRepaymentSchedule, Loan, LoanPayment
from administration.models import Transaction
from bank.models import Bank, BankPayment
from django.db import transaction
from django.db.models import Sum

from savings.models import Savings, SavingsPayment, DailyContribution

logger = logging.getLogger(__name__)
from django.db.models import F

class Command(BaseCommand):
    help = 'Find specific entries in the database, calculate the sum of the amount, delete the entries, and remove the amount from the balance'

    def handle(self, *args, **kwargs):
        try:
            models_to_recalculate = {
                'bank': 'bank.BankPayment',
            }

            for model_name, model_path in models_to_recalculate.items():
                try:
                    model = apps.get_model(model_path)
                    ledger = model_name
                    accounts = model.objects.values_list(f'{ledger}', flat=True).distinct()

                    for account_id in accounts:
                        payments = model.objects.filter(**{f'{ledger}': account_id}).order_by('payment_date', 'created_at').iterator()

                        previous_balance = Decimal('0.00')
                        batch_size = 100  # Process 100 rows at a time
                        updates = []

                        for payment in payments:
                            payment.bank_balance = previous_balance + payment.amount
                            previous_balance = payment.bank_balance
                            updates.append(payment)

                            if len(updates) >= batch_size:
                                model.objects.bulk_update(updates, ['bank_balance'])
                                updates = []
                            self.stdout.write(self.style.SUCCESS(f'Updated balance for {model_name}'))

                        if updates:
                            model.objects.bulk_update(updates, ['bank_balance'])
                            self.stdout.write(self.style.SUCCESS(f'Updated balance for {model_name}'))

                    self.stdout.write(self.style.SUCCESS(f'Successfully recalculated balances for {model_name}'))
                except LookupError:
                    self.stdout.write(self.style.ERROR(f'Model {model_path} not found'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error recalculating balances for {model_name}: {e}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error recalculating balances for all specified models: {e}'))
            logger.error(f'Error recalculating balances for all specified models: {e}')

        self.stdout.write(self.style.SUCCESS('Successfully recalculated balances for all specified models'))