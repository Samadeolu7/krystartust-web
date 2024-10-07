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
        models_to_recalculate = {
            'liability': 'liability.LiabilityPayment',
            'income': 'income.IncomePayment',
            'expense': 'expenses.ExpensePayment',
            'bank': 'bank.BankPayment',
            'savings': 'savings.SavingsPayment',
        }

        # Calculate the time range
        now = timezone.now()
        time_threshold = now - timedelta(hours=96)

        # Directory to save CSV files
        output_dir = 'output_csvs'
        os.makedirs(output_dir, exist_ok=True)

        # Query the database for entries created within the last 96 hours and write to CSV
        for model_name, model_path in models_to_recalculate.items():
            try:
                model = apps.get_model(model_path)
                recent_entries = model.objects.filter(created_at__range=(time_threshold, now))

                # Write results to CSV
                csv_file_path = os.path.join(output_dir, f'{model_name}_entries.csv')
                with open(csv_file_path, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    # Write header
                    writer.writerow([field.name for field in model._meta.fields])
                    # Write data rows
                    for entry in recent_entries:
                        writer.writerow([getattr(entry, field.name) for field in model._meta.fields])

                self.stdout.write(self.style.SUCCESS(f'Successfully wrote entries for {model_name} to {csv_file_path}'))
            except LookupError:
                self.stdout.write(self.style.ERROR(f'Model {model_path} not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error writing entries for {model_name} to CSV: {e}'))

        # Example for LoanPayment model
        try:
            recent_loan_payments = LoanPayment.objects.filter(created_at__range=(time_threshold, now))
            csv_file_path = os.path.join(output_dir, 'loan_payments_entries.csv')
            with open(csv_file_path, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                # Write header
                writer.writerow([field.name for field in LoanPayment._meta.fields])
                # Write data rows
                for payment in recent_loan_payments:
                    writer.writerow([getattr(payment, field.name) for field in LoanPayment._meta.fields])

            self.stdout.write(self.style.SUCCESS(f'Successfully wrote loan payments entries to {csv_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error writing loan payments entries to CSV: {e}'))