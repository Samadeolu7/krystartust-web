import calendar
from datetime import datetime
from django.shortcuts import render

from bank.models import Bank
from client.models import Client
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from savings.models import Savings, SavingsPayment
from main.models import ClientGroup as Group

# Create your views here.

def all_clients_report(request):
    clients = Client.objects.all()
    loans = Loan.objects.filter(client__in=clients)
    savings = Savings.objects.filter(client__in=clients)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'all_clients_report.html', context)

def all_groups_report(request):
    groups = Group.objects.all()
    clients = Client.objects.filter(group__in=groups)
    loans = Loan.objects.filter(client__in=clients)
    savings = Savings.objects.filter(client__in=clients)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'groups': groups,
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'all_groups_report.html', context)

def all_loans_report(request):
    loans = Loan.objects.all()
    clients = Client.objects.filter(loan__in=loans)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    context = {
        'loans': loans,
        'clients': clients,
        'loan_payments': loan_payments,
    }

    return render(request, 'all_loans_report.html', context)

def all_savings_report(request):
    savings = Savings.objects.all()
    clients = Client.objects.filter(savings__in=savings)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'savings': savings,
        'clients': clients,
        'savings_payments': savings_payments,
    }

    return render(request, 'all_savings_report.html', context)

def all_transactions_report(request):
    loan_payments = LoanPayment.objects.all()
    savings_payments = SavingsPayment.objects.all()
    loans = Loan.objects.filter(loan_payment__in=loan_payments)
    savings = Savings.objects.filter(savings_payment__in=savings_payments)
    clients = Client.objects.filter(loan__in=loans, savings__in=savings)
    context = {
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
        'loans': loans,
        'savings': savings,
        'clients': clients,
    }
    
    return render(request, 'all_transactions_report.html', context)

def daily_collection_form(request):
    return render(request, 'daily_collection_form.html')

def daily_transactions_report(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        schedule = LoanRepaymentSchedule.objects.filter(due_date=date)
        loan_payments = LoanPayment.objects.filter(payment_date=date)
        savings_payments = SavingsPayment.objects.filter(payment_date=date)
        context = {
            'Schedule': schedule,
            'loan_payments': loan_payments,
            'savings_payments': savings_payments,
        }
    else:
        return render(request, 'daily_collection_form.html')
    return render(request, 'daily_collection_report.html', context)

from django.db.models import Sum
from datetime import datetime
import calendar

def profit_and_loss_report(request):
    # Get the current year
    current_year = datetime.now().year

    # Get monthly totals for incomes and expenses using annotations
    incomes_by_month = IncomePayment.objects.filter(created_at__year=current_year).values(
        'payment_date__month', 'income__name'
    ).annotate(monthly_total=Sum('amount'))

    expenses_by_month = ExpensePayment.objects.filter(created_at__year=current_year).values(
        'payment_date__month', 'expense__name'
    ).annotate(monthly_total=Sum('amount'))

    # Initialize dictionaries for storing the data
    monthly_incomes = {month: {} for month in range(1, 13)}
    monthly_expenses = {month: {} for month in range(1, 13)}
    monthly_income_totals = {month: 0 for month in range(1, 13)}
    monthly_expense_totals = {month: 0 for month in range(1, 13)}

    yearly_income_by_type = {}
    yearly_expense_by_type = {}

    yearly_income_total = 0
    yearly_expense_total = 0

    # Process the incomes and calculate totals by month and type
    for income in incomes_by_month:
        month = income['payment_date__month']
        income_type = income['income__name']
        total = income['monthly_total']

        if income_type not in monthly_incomes[month]:
            monthly_incomes[month][income_type] = {'total': 0}

        monthly_incomes[month][income_type]['total'] += total
        monthly_income_totals[month] += total
        yearly_income_total += total

        # Yearly total by income type
        if income_type not in yearly_income_by_type:
            yearly_income_by_type[income_type] = 0
        yearly_income_by_type[income_type] += total

    # Process the expenses and calculate totals by month and type
    for expense in expenses_by_month:
        month = expense['payment_date__month']
        expense_type = expense['expense_type__name']
        total = expense['monthly_total']

        if expense_type not in monthly_expenses[month]:
            monthly_expenses[month][expense_type] = {'total': 0}

        monthly_expenses[month][expense_type]['total'] += total
        monthly_expense_totals[month] += total
        yearly_expense_total += total

        # Yearly total by expense type
        if expense_type not in yearly_expense_by_type:
            yearly_expense_by_type[expense_type] = 0
        yearly_expense_by_type[expense_type] += total

    # Create a list of tuples (month_number, month_name)
    months = [(month, calendar.month_name[month]) for month in range(1, 13)]

    context = {
        'monthly_incomes': monthly_incomes,
        'monthly_expenses': monthly_expenses,
        'monthly_income_totals': monthly_income_totals,
        'monthly_expense_totals': monthly_expense_totals,
        'yearly_income_total': yearly_income_total,
        'yearly_expense_total': yearly_expense_total,
        'yearly_income_by_type': yearly_income_by_type,
        'yearly_expense_by_type': yearly_expense_by_type,
        'months': months,  # List of tuples (month_number, month_name)
        'monthly_profit': {
            month: (monthly_income_totals.get(month, 0) - monthly_expense_totals.get(month, 0))
            for month in range(1, 13)
        }
    }

    return render(request, 'profit_loss.html', context)

def trial_balance_report(request):

    # Initialize dictionaries to hold totals by account type
    incomes = Income.objects.all()
    expenses = Expense.objects.all()
    savings = Savings.objects.all()
    loans = Loan.objects.all()
    banks = Bank.objects.all()

    total_savings = 0
    total_loans = 0
    total_incomes = 0
    total_expenses = 0
    total_banks = 0

    for saving in savings:
        total_savings += saving.balance

    for loan in loans:
        total_loans += loan.balance

    for income in incomes:
        total_incomes += income.balance

    for expense in expenses:
        total_expenses += expense.balance

    for bank in banks:
        total_banks += bank.balance

    total_credit = total_incomes + total_savings 
    total_debit = total_expenses + total_loans + total_banks

    context = {
        'total_savings': total_savings,
        'total_loans': total_loans,
        'total_incomes': total_incomes,
        'total_expenses': total_expenses,
        'total_banks': total_banks,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'banks': banks,
        'incomes': incomes,

    }
    return render(request, 'trial_balance.html', context)
