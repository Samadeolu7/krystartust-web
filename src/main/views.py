import json
from datetime import datetime, timedelta
from subprocess import Popen

from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.conf import settings

from administration.decorators import allowed_users
from administration.models import Approval, Notification, Tickets, Transaction
from bank.models import Bank, BankPayment
from client.models import Client
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule as LoanRepayment
from main.utils import close_balance_sheet, close_bank, close_liability, close_loan_repayment, close_savings, close_trial_balance, close_year, verify_trial_balance
from savings.models import Savings, SavingsPayment
from user.models import User

from .models import ClientGroup as Group, JournalEntry, Year
from .forms import GroupForm, JVForm
from django.core.cache import cache
from django.db.models.functions import ExtractWeek
from django.contrib import messages

from django.contrib.contenttypes.models import ContentType
from django.db import transaction


@login_required
def dashboard(request):
    """View to render the main dashboard."""
    
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=5)  # Includes up to Friday
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(day=28) + timedelta(days=4)  # this will never fail

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
        Q(due_date__range=[start_of_month, end_of_month]) | 
        Q(payment_date__range=[start_of_month, end_of_month])
    ).values('amount_due', 'due_date', 'payment_date')

    expected_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['due_date'] and start_of_week <= repayment['due_date'] <= end_of_week
    )
    actual_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['payment_date'] and start_of_week <= repayment['payment_date'] <= end_of_week
    )
    daily_expected_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['due_date'] and today == repayment['due_date']
    )
    daily_actual_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['payment_date'] and today == repayment['payment_date']
    )
    end_of_month = today.replace(day=28) + timedelta(days=4)  # this will never fail
    monthly_expected_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['due_date'] and start_of_month <= repayment['due_date'] <= end_of_month
    )
    monthly_actual_cash_in = sum(
        repayment['amount_due'] for repayment in loan_repayments 
        if repayment['payment_date'] and start_of_month <= repayment['payment_date'] <= end_of_month
    )


    # Initialize lists to hold daily amounts for the current month
    days_in_month = (end_of_month - start_of_month).days + 1
    due_dates = [0] * days_in_month
    payment_dates = [0] * days_in_month

    for repayment in loan_repayments:
        if repayment['due_date'] and start_of_month <= repayment['due_date'] <= end_of_month:
            due_day = (repayment['due_date'] - start_of_month).days
            due_dates[due_day] += float(repayment['amount_due'])
        if repayment['payment_date'] and start_of_month <= repayment['payment_date'] <= end_of_month:
            payment_day = (repayment['payment_date'] - start_of_month).days
            payment_dates[payment_day] += float(repayment['amount_due'])


    current_defaulters = Loan.objects.with_is_defaulted().filter(is_defaulted=True).count()

    #count number of clients in client groups for each user assigned to them
    staff = User.objects.filter().all()
    group_clients = {}
    for user in staff:
        user_groups = Group.objects.filter(user=user)
        if user_groups:
            group_clients[user.username.split()[0]] = 0
            for group in user_groups:
                clients = Client.objects.filter(group=group)
                group_clients[user.username.split()[0]] += clients.count()

    

    # Determine user role for template context
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    is_manager = user.groups.filter(name='Manager').exists()
    is_employee = user.groups.filter(name='Staff').exists()

    approvals = 0
    open_tickets = 0
    
    if is_admin:
        approvals = Approval.objects.filter(approved=False,rejected=False).count()
        journal_entry_approvals = JournalEntry.objects.filter(approved=False,rejected=False).count()
        approvals += journal_entry_approvals
        open_tickets = Tickets.objects.filter(closed=False).count()
    if is_manager:
        approvals = Approval.objects.filter(approved=False,rejected=False,type='Loan').count()
        # check for open tickets where the user is one of the assigned employees
        open_tickets = Tickets.objects.filter(closed=False, users__in=[user]).count()

    if is_employee:
        approvals = Approval.objects.filter(approved=False,rejected=False,type='Loan').count()
        open_tickets = Tickets.objects.filter(closed=False, users__in=[user]).count()

    notifications = Notification.objects.filter(user=request.user, is_read=False)

    system_year = Year.current_year()
    date_year = today.year
    close_year = False
    if date_year > system_year:
        close_year = True
    
    context = {
        'user': user,
        'loan_types': loan_types,
        'total_amounts': total_amounts,
        'total_balances': total_balances,
        'weekly_inflows': weekly_inflows,
        'due_dates': due_dates,
        'payment_dates': payment_dates,
        'current_defaulters': current_defaulters,
        'expected_cash_in_weekly': expected_cash_in,
        'actual_cash_in_weekly': actual_cash_in,
        'expected_cash_in_daily': daily_expected_cash_in,
        'actual_cash_in_daily': daily_actual_cash_in,
        'expected_cash_in_monthly': monthly_expected_cash_in,
        'actual_cash_in_monthly': monthly_actual_cash_in,
        'is_admin': is_admin,
        'is_manager': is_manager,
        'is_employee': is_employee,
        'group_clients': group_clients,
        'approvals': approvals,
        'notifications': notifications,
        'open_tickets': open_tickets,
        'close_year': close_year,
    }

    return render(request, 'dash.html', context)


def fake_dashboard(request):
    context = {
        'static_url': settings.STATIC_URL,
        'base_url': settings.BASE_URL,
    }
    return render(request, 'payslip_template.html',context)


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
            return redirect('all_groups_report')
    else:
        form = GroupForm()
        
    
    return render(request, 'group_form.html', {'form': form})

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
    year = Year.current_year()
    type_value = request.GET.get('type')
    if type_value == 'Income':
        accounts = Income.objects.filter(year=year)
    elif type_value == 'Expense':
        accounts = Expense.objects.filter(year=year)
    elif type_value == 'Liability':
        accounts = Liability.objects.filter(year=year)
    elif type_value == 'Bank':
        accounts = Bank.objects.filter(year=year)
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
            created_by = request.user

            if credit_account == debit_account:
                messages.error(request, "Credit and debit accounts cannot be the same.")
                return redirect('journal_entry')
            
            # Classify the account types and make entries accordingly
            journal_entry = JournalEntry.objects.create(
                credit_account=ContentType.objects.get_for_model(credit_account),
                credit_id=credit_account.id,
                credit_amount=amount,
                debit_account=ContentType.objects.get_for_model(debit_account),
                debit_id=debit_account.id,
                debit_amount=amount,
                comment=description,
                payment_date=payment_date,
                approved=False,
                created_by=created_by
            )
            
            return redirect('dashboard')
    
    form = JVForm()
    return render(request, 'journal_entry.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def approve_journal_entry(request, pk):
    journal_entry = get_object_or_404(JournalEntry, id=pk)

    # Define classifications
    debit_side = ['bank', 'assets', 'expense']
    credit_side = ['savings', 'income', 'liability']

    with transaction.atomic():
        if not journal_entry.approved:
            journal_entry.approved = True
            journal_entry.save()

            credit_account = journal_entry.credit_object
            debit_account = journal_entry.debit_object
            amount = journal_entry.credit_amount
            description = journal_entry.comment
            payment_date = journal_entry.payment_date

            credit_account_type = journal_entry.credit_account.model
            debit_account_type = journal_entry.debit_account.model

            tran = Transaction(description=description)
            tran.save(prefix='JV')

            # Determine the direction of funds
            if credit_account_type in credit_side and debit_account_type in debit_side:
                # Standard credit and debit
                credit_account.record_payment(amount, description, payment_date, tran)
                debit_account.record_payment(amount, description, payment_date, tran)

            elif credit_account_type in debit_side and debit_account_type in credit_side:
                # Reverse credit and debit (unusual, but possible)
                credit_account.record_payment(-amount, description, payment_date, tran)
                debit_account.record_payment(-amount, description, payment_date, tran)

            elif credit_account_type in credit_side and debit_account_type in credit_side:
                # Credit on both sides (e.g., shifting liabilities)
                credit_account.record_payment(amount, description, payment_date, tran)
                debit_account.record_payment(-amount, description, payment_date, tran)

            elif credit_account_type in debit_side and debit_account_type in debit_side:
                # Debit on both sides (e.g., transferring assets)
                credit_account.record_payment(-amount, description, payment_date, tran)
                debit_account.record_payment(amount, description, payment_date, tran)

            else:
                messages.error(request, "Invalid account type combination.")
                return redirect('dashboard')

            verify_trial_balance()
        else:
            messages.error(request, 'Journal Entry has already been approved')
            return redirect('dashboard')

    return redirect('dashboard')


@login_required
@allowed_users(allowed_roles=['Admin'])
def disapprove_journal_entry(request, entry_id):
    journal_entry = get_object_or_404(JournalEntry, id=entry_id)
    if not journal_entry.approved:
        journal_entry.rejected = True
        journal_entry.save()
    
    return redirect('dashboard')

def test_html(request):
    # Example condition - you can replace this with your actual condition logic
    today = datetime.now()
    days_in_month = 30  # or use calendar.monthrange to get the exact number of days for a specific month/year
    
    # Dictionary to hold date and its condition (True if tick should be displayed)
    ticks = {}
    for i in range(days_in_month):
        date = today.replace(day=i + 1)  # Get each day of the month
        # Replace the condition below with your own logic
        ticks[date] = (date.day % 2 == 0)  # Example: tick every even day

    return render(request, 'test.html', {'ticks': ticks})


@login_required
def search(request):
    query = request.GET.get('q')
    clients = Client.objects.filter(name__icontains=query)
    transactions = Transaction.objects.filter(reference_number__icontains=query)
    bank_payments = BankPayment.objects.filter(transaction__in=transactions)
    savings_payment = SavingsPayment.objects.filter(transaction__in=transactions)
    loan_payment = LoanPayment.objects.filter(transaction__in=transactions)
    expense_payment = ExpensePayment.objects.filter(transaction__in=transactions)
    income_payment = IncomePayment.objects.filter(transaction__in=transactions)
    liability_payment = LiabilityPayment.objects.filter(transaction__in=transactions)

    payments = list(savings_payment) + list(loan_payment) + list(expense_payment) + list(income_payment) + list(liability_payment)+ list(bank_payments)
    context = {
        'clients': clients,
        'payments': payments,
        'query': query
    }
    return render(request, 'search_result.html', context)

@login_required
@allowed_users(allowed_roles=['Admin'])
def close_year_view(request):
    today = timezone.now().date()
    system_year = Year.current_year()
    if today.year == system_year+1:
        with transaction.atomic():
            
            close_year()

            verify_trial_balance()

        return redirect('dashboard')
    else:
        messages.error(request, 'You can only close the year after the current year has ended.')
        return JsonResponse({'error': 'You can only close the year after the current year has ended.'})
    


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def review_week(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    errors = []
    
# Loan payments
    loan_payments = LoanPayment.objects.filter(payment_date__range=[week_start, week_end])
    loan_payment_counts = loan_payments.values('loan__id', 'client__name').annotate(count=Count('id')).filter(count__gt=1)
    for loan_payment_count in loan_payment_counts:
        errors.append({
            'message': f'Client {loan_payment_count["client__name"]} has more than one loan payment in the week',
            'link': f'/loan/detail/{loan_payment_count["loan__id"]}/'
        })
    
    # Savings payments
    savings_payments = SavingsPayment.objects.filter(payment_date__range=[week_start, week_end])
    savings_payment_counts = savings_payments.values('client__id', 'client__name', 'payment_date', 'transaction_type').annotate(count=Count('id')).filter(count__gt=1)
    for savings_payment_count in savings_payment_counts:
        if savings_payment_count['transaction_type'] == SavingsPayment.WITHDRAWAL:
            errors.append({
                'message': f'Client {savings_payment_count["client__name"]} has more than one withdrawal on {savings_payment_count["payment_date"]}',
                'link': f'/savings/savings_detail/{savings_payment_count["client__id"]}/'
            })
        else:
            errors.append({
                'message': f'Client {savings_payment_count["client__name"]} has more than one savings payment on {savings_payment_count["payment_date"]}',
                'link': f'/savings/savings_detail/{savings_payment_count["client__id"]}/'
            })
    
    # Expense payments
    expense_payments = ExpensePayment.objects.filter(payment_date__range=[week_start, week_end])
    expense_payment_counts = expense_payments.values('expense__id', 'expense__name', 'payment_date').annotate(count=Count('id')).filter(count__gt=1)
    for expense_payment_count in expense_payment_counts:
        errors.append({
            'message': f'Expense {expense_payment_count["expense__name"]} has more than one payment on {expense_payment_count["payment_date"]}',
            'link': f'/expenses/detail/{expense_payment_count["expense__id"]}/'
        })
    
    # Liability payments
    liability_payments = LiabilityPayment.objects.filter(payment_date__range=[week_start, week_end])
    liability_payment_counts = liability_payments.values('liability__id', 'liability__name', 'payment_date').annotate(count=Count('id')).filter(count__gt=1)
    for liability_payment_count in liability_payment_counts:
        errors.append({
            'message': f'Liability {liability_payment_count["liability__name"]} has more than one payment on {liability_payment_count["payment_date"]}',
            'link': f'/liability/detail/{liability_payment_count["liability__id"]}/'
        })

    # Bank payments
    bank_payments = BankPayment.objects.filter(payment_date__range=[week_start, week_end], transaction__reference_number__startswith='TRF')
    bank_payment_counts = bank_payments.values('description', 'payment_date').annotate(count=Count('id')).filter(count__gt=1)
    for bank_payment_count in bank_payment_counts:
        errors.append({
            'message': f'Transfer {bank_payment_count["description"]} has more than one payment on {bank_payment_count["payment_date"]}',
            'link': f'/bank/bank_payments/'
        })
    
    context = {
        'errors': errors,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'review_week.html', context)