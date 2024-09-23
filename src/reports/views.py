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
        loans = Loan.objects.filter(loan_payment__in=loan_payments)
        savings = Savings.objects.filter(savings_payment__in=savings_payments)
        clients = Client.objects.filter(loan__in=loans, savings__in=savings)
        context = {
            'Schedule': schedule,
            'loan_payments': loan_payments,
            'savings_payments': savings_payments,
            'loans': loans,
            'savings': savings,
            'clients': clients,
        }
    else:
        return render(request, 'daily_collection_form.html')
    return render(request, 'daily_transactions_report.html', context)


def profit_and_loss_report(request):
    # Get the current year
    current_year = datetime.now().year

    # Initialize dictionaries to hold monthly data
    monthly_incomes = {month: {} for month in range(1, 13)}
    monthly_expenses = {month: [] for month in range(1, 13)}
    expense_buckets = {month: {} for month in range(1, 13)}
    monthly_income_totals = {month: 0 for month in range(1, 13)}
    monthly_expense_totals = {month: 0 for month in range(1, 13)}

    # Initialize yearly totals
    yearly_income_total = 0
    yearly_expense_total = 0

    # Initialize dictionaries to hold yearly totals by type
    yearly_income_by_type = {}
    yearly_expense_by_type = {}

    # Get all incomes and expenses for the current year
    incomes = IncomePayment.objects.filter(created_at__year=current_year)
    expenses = ExpensePayment.objects.filter(created_at__year=current_year)

    # Organize incomes by month and income type, and calculate totals
    for income in incomes:
        month = income.payment_date.month
        income_type_name = income.income.name
        if income_type_name not in monthly_incomes[month]:
            monthly_incomes[month][income_type_name] = {'total': 0, 'details': []}
        monthly_incomes[month][income_type_name]['details'].append(income)
        monthly_incomes[month][income_type_name]['total'] += income.amount
        monthly_income_totals[month] += income.amount
        yearly_income_total += income.amount

        # Calculate yearly totals by income type
        if income_type_name not in yearly_income_by_type:
            yearly_income_by_type[income_type_name] = 0
        yearly_income_by_type[income_type_name] += income.amount

    # Organize expenses by month and calculate totals
    for expense in expenses:
        month = expense.payment_date.month
        monthly_expenses[month].append(expense)
        monthly_expense_totals[month] += expense.amount
        expense_type_name = expense.expense_type.name
        if expense_type_name not in expense_buckets[month]:
            expense_buckets[month][expense_type_name] = []
        expense_buckets[month][expense_type_name].append(expense)
        yearly_expense_total += expense.amount

        # Calculate yearly totals by expense type
        if expense_type_name not in yearly_expense_by_type:
            yearly_expense_by_type[expense_type_name] = 0
        yearly_expense_by_type[expense_type_name] += expense.amount

    # Create a list of tuples (month_number, month_name)
    months = [(month, calendar.month_name[month]) for month in range(1, 13)]
    
    context = {
        'monthly_incomes': monthly_incomes,
        'monthly_expenses': monthly_expenses,
        'expense_buckets': expense_buckets,
        'monthly_income_totals': monthly_income_totals,
        'monthly_expense_totals': monthly_expense_totals,
        'yearly_income_total': yearly_income_total,
        'yearly_expense_total': yearly_expense_total,
        'yearly_income_by_type': yearly_income_by_type,
        'yearly_expense_by_type': yearly_expense_by_type,
        'months': months,  # List of tuples (month_number, month_name)
    }
    return render(request, 'profit_loss.html', context)

def trial_balance_report(request):
    # Get the current year
    current_year = datetime.now().year

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