from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

import pytz
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

class Command(BaseCommand):
    help = 'Find specific entries in the database, calculate the sum of the amount, delete the entries, and remove the amount from the balance'

    def handle(self, *args, **kwargs):
        try:
            # Find IncomePayments from 655 to 670 and calculate the sum of the amount for each income
            income_total = {}
            income_payments = IncomePayment.objects.filter(id__range=[655, 670])
            for payment in income_payments:
                if payment.income_id not in income_total:
                    income_total[payment.income_id] = 0
                income_total[payment.income_id] += payment.amount
                payment.delete()
            logger.info('Income Total: %s', income_total)

            # Find BankPayments from 2544 to 2563 and calculate the sum of the amount for each bank
            bank_total = {}
            bank_payments = BankPayment.objects.filter(id__range=[2544, 2563])
            for payment in bank_payments:
                if payment.bank_id not in bank_total:
                    bank_total[payment.bank_id] = 0
                bank_total[payment.bank_id] += payment.amount
                payment.delete()
            logger.info('Bank Total: %s', bank_total)

            # Find LiabilityPayments from 100 to 103 and calculate the sum of the amount for each liability
            liability_total = {}
            liability_payments = LiabilityPayment.objects.filter(id__range=[100, 103])
            for payment in liability_payments:
                if payment.liability_id not in liability_total:
                    liability_total[payment.liability_id] = 0
                liability_total[payment.liability_id] += payment.amount
                payment.delete()
            logger.info('Liability Total: %s', liability_total)

            # Remove the amount from the balance
            for income_id, amount in income_total.items():
                with transaction.atomic():
                    income = Income.objects.select_for_update().get(id=income_id)
                    income.balance -= amount
                    income.save()

            for bank_id, amount in bank_total.items():
                with transaction.atomic():
                    bank = Bank.objects.select_for_update().get(id=bank_id)
                    bank.balance -= amount
                    bank.save()

            for liability_id, amount in liability_total.items():
                with transaction.atomic():
                    liability = Liability.objects.select_for_update().get(id=liability_id)
                    liability.balance -= amount
                    liability.save()

            logger.info('Done')
        except Exception as e:
            logger.error('An error occurred: %s', e)
            raise