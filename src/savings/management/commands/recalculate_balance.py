# management/commands/recalculate_balances.py

from django.core.management.base import BaseCommand
from decimal import Decimal
from django.apps import apps
from django.db import transaction
from loan.models import LoanPayment, Loan

class Command(BaseCommand):
    help = 'Recalculate and correct the balance values in all specified models'

    def handle(self, *args, **kwargs):
        models_to_recalculate = {
            'liability': 'liability.LiabilityPayment',
            'income': 'income.IncomePayment',
            'expense': 'expenses.ExpensePayment',
            'bank': 'bank.BankPayment',
            'savings': 'savings.SavingsPayment',
        }

        for model_name, model_path in models_to_recalculate.items():
            try:
                model = apps.get_model(model_path)
                ledger = model_name
                accounts = model.objects.values_list(f'{ledger}', flat=True).distinct()
                
                for account_id in accounts:
                    payments = model.objects.filter(**{f'{ledger}': account_id}).order_by('payment_date', 'created_at')
                    previous_balance = Decimal('0.00')
                    
                    with transaction.atomic():
                        for payment in payments:
                            payment.balance = previous_balance + payment.amount
                            payment.save()
                            previous_balance = payment.balance

                self.stdout.write(self.style.SUCCESS(f'Successfully recalculated balances for {model_name}'))
            except LookupError:
                self.stdout.write(self.style.ERROR(f'Model {model_path} not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error recalculating balances for {model_name}: {e}'))

        loans = Loan.objects.all()
        for loan in loans:
            payments = LoanPayment.objects.filter(loan=loan).order_by('payment_date', 'created_at')
            previous_balance = loan.amount * Decimal(1+(loan.interest/100))
            
            with transaction.atomic():
                for payment in payments:
                    payment.balance = previous_balance - payment.amount
                    payment.save()
                    previous_balance = payment.balance

        self.stdout.write(self.style.SUCCESS(f'Successfully recalculated balances for {loan}'))

        self.stdout.write(self.style.SUCCESS('Successfully recalculated balances for all specified models'))