import json
from datetime import timedelta
from subprocess import Popen

from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q
from django.utils import timezone

from administration.decorators import allowed_users
from bank.models import Bank
from client.models import Client
from expenses.models import Expense
from income.models import Income
from liability.models import Liability
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule as LoanRepayment
from savings.models import Savings, SavingsPayment

from .models import ClientGroup as Group
from .forms import GroupForm, JVForm
from django.core.cache import cache
from django.db.models.functions import ExtractWeek



@login_required
def update_app(request):
    # Run the Docker commands to update the app
    Popen(["docker-compose", "down"])
    Popen(["git", "pull", "origin", "main"])
    Popen(["docker-compose", "up", "--build", "-d"])
    return HttpResponse("App is updating. Please wait...")


@login_required
def dashboard(request):
    """View to render the main dashboard."""
    
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=5)  # Includes up to Friday

    # Retrieve or cache total loan data
    total_loan_data = cache.get('total_loan_data')
    if total_loan_data is None:
        total_loan_data = Loan.objects.values('loan_type').annotate(
            total_amount=Sum('amount'),
            total_balance=Sum('balance')
        )
        cache.set('total_loan_data', total_loan_data, timeout=3600)

    loan_types = [loan['loan_type'] for loan in total_loan_data]
    total_amounts = [loan['total_amount'] or 0 for loan in total_loan_data]
    total_balances = [loan['total_balance'] or 0 for loan in total_loan_data]

    # Calculate weekly inflows from Savings and Loan Payments
    weekly_inflows = [0] * 7  # Array for 7 days of the week

    savings_inflows = (
        SavingsPayment.objects.filter(payment_date__range=[start_of_week, today])
        .values('payment_date')
        .annotate(total=Sum('amount'))
    )

    loan_payment_inflows = (
        LoanPayment.objects.filter(payment_date__range=[start_of_week, today])
        .values('payment_date')
        .annotate(total=Sum('amount'))
    )

    transactions = list(savings_inflows) + list(loan_payment_inflows)
    for transaction in transactions:
        day_of_week = transaction['payment_date'].weekday()
        weekly_inflows[day_of_week] += transaction['total']

    # Calculate expected and actual cash inflows for the current week
    loan_repayments = LoanRepayment.objects.filter(
        Q(due_date__range=[start_of_week, end_of_week]) | 
        Q(payment_date__range=[start_of_week, end_of_week])
    ).values('amount_due', 'due_date', 'payment_date')

    expected_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['due_date'] and start_of_week <= repayment['due_date'] <= end_of_week
    )
    actual_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['payment_date'] and start_of_week <= repayment['payment_date'] <= end_of_week
    )

    # Calculate yearly inflows by week for visualization
    start_of_month = today.replace(day=1)
    next_month = today.replace(day=28) + timedelta(days=4)  # this will never fail
    end_of_month = next_month - timedelta(days=next_month.day)

    # Initialize lists to hold daily amounts for the current month
    days_in_month = (end_of_month - start_of_month).days + 1
    due_dates = [0] * days_in_month
    payment_dates = [0] * days_in_month

    for repayment in loan_repayments:
        if repayment['due_date'] and start_of_month <= repayment['due_date'] <= end_of_month:
            due_day = (repayment['due_date'] - start_of_month).days
            due_dates[due_day] += repayment['amount_due']
        if repayment['payment_date'] and start_of_month <= repayment['payment_date'] <= end_of_month:
            payment_day = (repayment['payment_date'] - start_of_month).days
            payment_dates[payment_day] += repayment['amount_due']

    current_defaulters = Loan.objects.with_is_defaulted().filter(is_defaulted=True).count()

    # Determine user role for template context
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    is_manager = user.groups.filter(name='Manager').exists()
    is_employee = user.groups.filter(name='Staff').exists()

    context = {
        'user': user,
        'loan_types': loan_types,
        'total_amounts': total_amounts,
        'total_balances': total_balances,
        'weekly_inflows': weekly_inflows,
        'due_dates': due_dates,
        'payment_dates': payment_dates,
        'current_defaulters': current_defaulters,
        'expected_cash_in': expected_cash_in,
        'actual_cash_in': actual_cash_in,
        'is_admin': is_admin,
        'is_manager': is_manager,
        'is_employee': is_employee,
    }

    return render(request, 'dash.html', context)


def fake_dashboard(request):
    return render(request, 'dashboard.html')


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def group_detail(request, pk):
    group = Client.objects.get(group=pk)
    return render(request, 'group_detail.html', {'group': group})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_view')
    else:
        form = GroupForm()
        
    
    return render(request, 'group_form.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def group_view(request):
    groups = Group.objects.all()
    return render(request, 'group_view.html', {'groups': groups})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def group_edit(request, pk):
    group = Group.objects.get(pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_view')
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'group_form.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def group_report(request, pk):
    group = Group.objects.get(pk=pk)
    clients = Client.objects.filter(group=group)
    loans = Loan.objects.filter(client__in=clients)
    savings = Savings.objects.filter(client__in=clients)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'group': group,
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'group_report.html', context)

# views.py


def get_accounts(request):
    type_value = request.GET.get('type')
    if type_value == 'Income':
        accounts = Income.objects.all()
    elif type_value == 'Expense':
        accounts = Expense.objects.all()
    elif type_value == 'Liability':
        accounts = Liability.objects.all()
    elif type_value == 'Bank':
        accounts = Bank.objects.all()
    else:
        accounts = []

    html = render_to_string('account_options.html', {'accounts': accounts})
    return JsonResponse(html, safe=False)

@login_required
@allowed_users(allowed_roles=['Admin'])
def journal_entry(request):
    if request.method == 'POST':
        form = JVForm(request.POST)
        if form.is_valid():
            credit_account = form.cleaned_data['jv_credit_account']
            debit_account = form.cleaned_data['jv_debit_account']
            amount = form.cleaned_data['amount']
            payment_date = form.cleaned_data['payment_date']
            description = form.cleaned_data['description']
            credit_account_type = form.cleaned_data['jv_credit']
            debit_account_type = form.cleaned_data['jv_debit']
            if credit_account == debit_account:
                return redirect('journal_entry')
            
            if credit_account_type == 'Income' and debit_account_type == 'Liability' or credit_account_type == 'Liability' and debit_account_type == 'Income':
                credit_account.record_payment(-amount,description,payment_date)
                debit_account.record_payment(amount,description,payment_date)
                return redirect('dashboard')
            
            elif credit_account_type == 'Income' or credit_account_type == 'Liability':
                credit_account.record_payment(-amount,description,payment_date)
                debit_account.record_payment(-amount,description,payment_date)
                return redirect('dashboard')

            elif debit_account_type == 'Income' or debit_account_type == 'Liability':
                
                credit_account.record_payment(amount,description,payment_date)
                debit_account.record_payment(amount,description,payment_date)
                return redirect('dashboard')
            else:
                credit_account.record_payment(-amount,description,payment_date)
                debit_account.record_payment(amount,description,payment_date)

            return redirect('dashboard')    
    
    form = JVForm()
    return render(request, 'journal_entry.html', {'form': form})