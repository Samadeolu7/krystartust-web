import calendar
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import render

from administration.decorators import allowed_users
from bank.models import Bank
from client.models import Client
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from reports.excel_utils import client_list_to_excel, client_loans_payments_to_excel, client_savings_payments_to_excel, defaulter_report_to_excel
from savings.models import Savings, SavingsPayment
from main.models import ClientGroup as Group
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
# Create your views here.


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
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

@login_required
def all_groups_report(request):
    groups = Group.objects.all()
    
    context = {
        'groups': groups,
    }
    return render(request, 'all_groups_report.html', context)

@login_required
def individual_group_report(request, group_id):
    group = Group.objects.get(pk=group_id)
    clients = Client.objects.filter(group=group)
    loans = Loan.objects.filter(client__in=clients)
    
    savings = Savings.objects.filter(client__in=clients)
    total_loans = loans.aggregate(total=Sum('amount')).get('total', 0) or 0
    total_loans_balance = loans.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_savings = savings.aggregate(total=Sum('balance')).get('total', 0) or 0
    
    # Calculate the new field for each loan
    for loan in loans:
        loan.total_with_interest = loan.amount * Decimal(1 + loan.interest / 100)
    
    context = {
        'group': group,
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'total_loans': total_loans,
        'total_loans_balance': total_loans_balance,
        'total_savings': total_savings,
    }

    return render(request, 'individual_group_report.html', context)

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
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

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
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

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
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

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def daily_collection_form(request):
    return render(request, 'daily_collection_form.html')


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
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


@login_required
@allowed_users(allowed_roles=['Admin'])
def profit_and_loss_report(request):
    current_year = datetime.now().year

    incomes_by_month = IncomePayment.objects.filter(created_at__year=current_year).values(
        'payment_date__month', 'income__name'
    ).annotate(monthly_total=Sum('amount'))

    expenses_by_month = ExpensePayment.objects.filter(created_at__year=current_year).values(
        'payment_date__month', 'expense__name', 'expense__expense_type__name'  # Include expense name
    ).annotate(monthly_total=Sum('amount'))

    monthly_incomes = {month: {} for month in range(1, 13)}
    monthly_expenses = {month: {} for month in range(1, 13)}
    monthly_income_totals = {month: 0 for month in range(1, 13)}
    monthly_expense_totals = {month: 0 for month in range(1, 13)}

    yearly_income_by_type = {}
    yearly_expense_by_type = {}

    yearly_income_total = 0
    yearly_expense_total = 0

    # Process incomes
    for income in incomes_by_month:
        month = income['payment_date__month']
        income_type = income['income__name']
        total = income['monthly_total']

        if income_type not in monthly_incomes[month]:
            monthly_incomes[month][income_type] = {'total': 0}

        monthly_incomes[month][income_type]['total'] += total
        monthly_income_totals[month] += total
        yearly_income_total += total

        if income_type not in yearly_income_by_type:
            yearly_income_by_type[income_type] = 0
        yearly_income_by_type[income_type] += total

    # Process expenses, track each individual expense separately
    for expense in expenses_by_month:
        month = expense['payment_date__month']
        expense_type = expense['expense__expense_type__name']
        expense_name = expense['expense__name']
        total = expense['monthly_total']

        if expense_type not in monthly_expenses[month]:
            monthly_expenses[month][expense_type] = {'total': 0, 'expenses': {}}



        if expense_name not in monthly_expenses[month][expense_type]['expenses']:
            monthly_expenses[month][expense_type]['expenses'][expense_name] = {month: 0 for month in range(1, 13)}
            monthly_expenses[month][expense_type]['expenses'][expense_name]['year'] = 0

        monthly_expenses[month][expense_type]['expenses'][expense_name][month] = expense['monthly_total']
        monthly_expenses[month][expense_type]['expenses'][expense_name]['year'] += expense['monthly_total']


        monthly_expenses[month][expense_type]['total'] += total
        monthly_expense_totals[month] += total
        yearly_expense_total += total

        if expense_type not in yearly_expense_by_type:
            yearly_expense_by_type[expense_type] = 0
        
        yearly_expense_by_type[expense_type] += total

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
        'months': months,
        'monthly_profit': {
            month: (monthly_income_totals.get(month, 0) - monthly_expense_totals.get(month, 0))
            for month in range(1, 13)
        }
    }

    return render(request, 'profit_loss.html', context)


@login_required
@allowed_users(allowed_roles=['Admin'])
def trial_balance_report(request):
    # Fetch all objects
    incomes = Income.objects.all()
    expenses = Expense.objects.all()
    banks = Bank.objects.all()
    liability = Liability.objects.all()

    # Aggregate sums in a single query for each model
    total_incomes = Income.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_expenses = Expense.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_savings = Savings.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_loans = Loan.objects.filter(approved=True).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_banks = Bank.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_liability = Liability.objects.aggregate(total=Sum('balance')).get('total', 0) or 0

    # Calculate total credit and debit
    total_credit = total_incomes + total_savings + total_liability
    total_debit = total_expenses + total_loans + total_banks 

    context = {
        'total_savings': total_savings,
        'total_loans': total_loans,
        'total_incomes': total_incomes,
        'total_expenses': total_expenses,
        'total_banks': total_banks,
        'total_liability': total_liability,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'banks': banks,
        'incomes': incomes,
        'expenses': expenses,
        'liabilities': liability,
    }
    return render(request, 'trial_balance.html', context)


@login_required
@allowed_users(allowed_roles=['Admin'])
def client_list_excel(request):
    merged_df = client_list_to_excel()
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=client_list.xlsx'
    merged_df.to_excel(response, index=False)
    return response

@login_required
@allowed_users(allowed_roles=['Admin'])
def defaulter_report_excel(request):
    df = defaulter_report_to_excel()
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=defaulter_report.xlsx'
    df.to_excel(response, index=False)
    return response

@login_required
@allowed_users(allowed_roles=['Admin'])
def client_savings_payments_excel(request, client_id):
    client = Client.objects.get(pk=client_id)
    df = client_savings_payments_to_excel(client)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={client.name}_savings_payments.xlsx'
    df.to_excel(response, index=False)
    return response

@login_required
@allowed_users(allowed_roles=['Admin'])
def client_loans_payments_excel(request, client_id):
    client = Client.objects.get(pk=client_id)
    df = client_loans_payments_to_excel(client)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={client.name}_loans_payments.xlsx'
    df.to_excel(response, index=False)
    return response

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def weekly_cash_flow_report(request):
    # Get the current date
    today = datetime.now()
    
    # Initialize dictionaries to store weekly totals
    weekly_incomes = {week: 0 for week in range(1, 6)}
    weekly_expenses = {week: 0 for week in range(1, 6)}
    weekly_loan_payments = {week: 0 for week in range(1, 6)}
    weekly_savings_payments = {week: 0 for week in range(1, 6)}
    accumulated_savings = {week: 0 for week in range(1, 6)}

    # Iterate over the past 5 weeks
    five_weeks_ago = today - timedelta(weeks=5)
    total = SavingsPayment.objects.filter(payment_date__lt=five_weeks_ago).aggregate(total=Sum('amount'))['total'] or 0
    for week in range(5):
        start_date = five_weeks_ago + timedelta(weeks=week)
        end_date = five_weeks_ago + timedelta(weeks=week+1)
        
        weekly_savings_payments[week+1] = SavingsPayment.objects.filter(
            payment_date__gte=start_date, payment_date__lt=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Accumulate savings payments
        if week == 0:
            accumulated_savings[week+1] = weekly_savings_payments[week+1] + total
        else:
            accumulated_savings[week+1] = accumulated_savings[week] + weekly_savings_payments[week+1]

    context = {
        'weekly_incomes': weekly_incomes,
        'weekly_expenses': weekly_expenses,
        'weekly_loan_payments': weekly_loan_payments,
        'weekly_savings_payments': weekly_savings_payments,
        'accumulated_savings': accumulated_savings,
    }

    return render(request, 'weekly_cash_flow_report.html', context)