# management/commands/fix_payments.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from bank.models import BankPayment
from bank.utils import get_cash_in_hand
from income.models import IncomePayment
from django.db import transaction

from liability.utils import create_union_contribution_income_payment

class Command(BaseCommand):
    help = 'Fix payments that did not hit the bank'

    def handle(self, *args, **kwargs):
        # Define the payments that need to be fixed
        payments_to_fix = [
            {
                'id': 263,
                'description': 'from Morenikeji Idowu',
                'amount': 1400,
                'payment_date': '2024-09-27'
            },
            {
                'id': 261,
                'description': 'from Comfort Alimi',
                'amount': 1200,
                'payment_date': '2024-09-27'
            },
            {
                'id': 259,
                'description': 'from Olajumoke Kolawole',
                'amount': 2000,
                'payment_date': '2024-09-27'
            },
            {
                'id': 257,
                'description': 'from Ogunfowora Olayemi',
                'amount': 1600,
                'payment_date': '2024-09-20'
            },
            {
                'id': 255,
                'description': 'from Omobolaji Bosede Amadi',
                'amount': 2000,
                'payment_date': '2024-09-20'
            },
            {
                'id': 253,
                'description': 'from Olawunmi Folorunsho',
                'amount': 2000,
                'payment_date': '2024-09-20'
            }
        ]

        # Fix the payments
        for payment in payments_to_fix:
            try:

                create_union_contribution_income_payment(payment['payment_date'], payment['description'])


                self.stdout.write(self.style.SUCCESS(f'Successfully fixed payment for {payment["description"]}'))
            except IncomePayment.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'IncomePayment with id {payment["id"]} does not exist'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fixing payment for {payment["description"]}: {e}'))