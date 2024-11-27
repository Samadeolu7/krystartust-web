from bank.models import Bank
from expenses.models import Expense
from income.models import Income
from liability.models import Liability
from loan.models import Loan
from savings.models import Savings

from django.db.models import Sum


def verify_trial_balance():

    # Aggregate sums in a single query for each model
    total_incomes = Income.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_expenses = Expense.objects.filter(approved=True).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_savings = Savings.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_loans = Loan.objects.filter(approved=True).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_banks = Bank.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_liability = Liability.objects.aggregate(total=Sum('balance')).get('total', 0) or 0

    # Calculate total credit and debit
    total_credit = total_incomes + total_savings + total_liability
    total_debit = total_expenses + total_loans + total_banks 

    if total_credit == total_debit:
        return True
    else:
        raise ValueError('Trial balance does not match')
    
    