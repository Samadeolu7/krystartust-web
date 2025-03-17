import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

# Create your views here.
from django.shortcuts import render

from administration.decorators import allowed_users
from administration.models import Approval, Transaction
from administration.utils import validate_month_status
from main.models import ClientGroup
from main.utils import verify_trial_balance
from savings.utils import create_dc_payment, make_withdrawal, setup_monthly_contributions
from .models import ClientContribution, DailyContribution, Savings, SavingsPayment
from .forms import DCForm, DailyContributionSpreadsheetForm, MultiDayContributionForm, SavingsForm, WithdrawalForm, CompulsorySavingsForm, SavingsExcelForm, CombinedPaymentForm, ToggleDailyContributionForm, SetupMonthlyContributionsForm, ClientContributionForm
from .excel_utils import savings_from_excel
from bank.utils import create_bank_payment
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .forms import MonthYearForm  # Import the new form


@login_required
@allowed_users(allowed_roles=['Admin'])
def compulsory_savings(request):
    if request.method == 'POST':
        form = CompulsorySavingsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = CompulsorySavingsForm()
        title = 'Compulsory Savings'
        return render(request, 'fees.html', {'form': form,'title': title})

@login_required
def savings_detail(request, client_id):
    ajo = ClientGroup.objects.filter(name='Ajo').first()
    id = ajo.id
    
    referring_page = request.META.get('HTTP_REFERER')
    if referring_page and f'/reports/individual-group-report/{id}' in referring_page:
        savings = Savings.objects.filter(client_id=client_id, type=Savings.DC).first()
    else:
        savings = Savings.objects.filter(client_id=client_id).first()
    
    
    # Filter the savings payments using the savings IDs
    savings_payments = SavingsPayment.objects.filter(savings_id=savings.id)
    
    context = {
        'savings': savings,
        'savings_payments': savings_payments,
        'client_id': client_id
    }
    return render(request, 'savings_detail.html', context)


@login_required
def register_payment(request):
    if request.method == 'POST':
        form = CombinedPaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                tran_date = form.cleaned_data['payment_date']
                try:
                    validate_month_status(tran_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'combined_payment_form.html', {'form': form})
                loan,savings = form.save()
                bank = form.cleaned_data['bank']
                create_bank_payment(
                    bank=bank,
                    description=f"Combined Savings and Loan Payment by {savings.client.name}",
                    amount=savings.amount+loan.amount,
                    payment_date=form.cleaned_data['payment_date'],
                    transaction=savings.transaction,
                    created_by=request.user
                )
                verify_trial_balance()
            
            return redirect('dashboard')
    else:
        form = CombinedPaymentForm()
    return render(request, 'combined_payment_form.html', {'form': form})


@login_required
def register_savings(request):
    if request.method == 'POST':
        form = SavingsForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payment_date = form.cleaned_data['payment_date']

                try:
                    validate_month_status(payment_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'savings_form.html', {'form': form})
                
                if form.cleaned_data['amount'] < 0:
                    make_withdrawal(form, request.user)
                    return redirect('dashboard')
                savings = form.save(commit=False)
                tran = Transaction(description=f'Savings for {savings.client.name}')
                tran.save(prefix='SVS')
                savings.transaction = tran
                savings.save()
                create_bank_payment(
                    bank=form.cleaned_data['bank'],
                    description=f"Savings Payment by {savings.client.name}",
                    amount=form.cleaned_data['amount'],
                    payment_date=form.cleaned_data['payment_date'],
                    transaction=tran,
                    created_by=request.user
                )
                verify_trial_balance()
            messages.success(request, 'Savings registered successfully')    
            
            return redirect('dashboard')
        else:
            messages.error(request, f'An error occurred while registering savings {form.errors}')

    else:
        form = SavingsForm()
    return render(request, 'savings_form.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def record_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payment_date = form.cleaned_data['payment_date']
                try:
                    validate_month_status(payment_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'withdrawal_form.html', {'form': form})
                
                if form.cleaned_data['amount'] > form.cleaned_data['savings'].balance:
                    messages.error(request, 'Insufficient balance')
                    return redirect('savings_withdrawal')
                
                make_withdrawal(form, request.user)
                verify_trial_balance()

            return redirect('dashboard')
    else:
        form = WithdrawalForm()
    return render(request, 'withdrawal_form.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def upload_savings(request):
    if request.method == 'POST':
        form = SavingsExcelForm(request.POST, request.FILES)
        if form.is_valid():
            report_path = savings_from_excel(request.FILES['excel_file'])

            # Read the report file content
            with open(report_path, 'r') as report_file:
                report_content = report_file.read()

            # Create a downloadable response
            response = HttpResponse(report_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="savings_report.csv"'
            return response
    else:
        form = SavingsExcelForm()
    return render(request, 'upload_savings.html', {'form': form})


@login_required
def setup_monthly_contributions_view(request):
    if request.method == 'POST':
        form = SetupMonthlyContributionsForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.setup_monthly_contributions(request.user)
                verify_trial_balance()
            return redirect('dashboard')
    else:
        form = SetupMonthlyContributionsForm()
    return render(request, 'setup_monthly_contributions.html', {'form': form})

@login_required
def toggle_daily_contribution_view(request):
    if request.method == 'POST':
        form = ToggleDailyContributionForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                form.save(request)
                verify_trial_balance()
            return redirect('dashboard')
    else:
        form = ToggleDailyContributionForm()
    return render(request, 'toggle_daily_contribution.html', {'form': form})

@login_required
def record_client_contribution(request):
    if request.method == 'POST':
        form = ClientContributionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ClientContributionForm()
    return render(request, 'record_client_contribution.html', {'form': form})

@login_required
def multi_day_contribution_view(request):
    if request.method == 'POST':
        form = MultiDayContributionForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('daily_contribution_spreadsheet')
        else:
            messages.error(request, 'An error occurred while saving the contributions, invalid form data')
    else:
        form = MultiDayContributionForm()

    context = {
        'form': form
    }
    return render(request, 'multi_day_contribution.html', context)


@login_required
def fetch_contributions(request, client_contribution_id):
    client_contribution = get_object_or_404(ClientContribution, id=client_contribution_id)
    today = datetime.date.today()
    month = today.month
    year = today.year
    daily_contributions = DailyContribution.objects.filter(client_contribution=client_contribution, date__month=month, date__year=year)
    contributions = [
        {
            'date': contribution.date.strftime('%Y-%m-%d'),
            'amount': contribution.client_contribution.amount,
            'payment_made': contribution.payment_made
        }
        for contribution in daily_contributions
    ]
    return JsonResponse({'contributions': contributions})


def calculate_monthly_totals(client_contribution):
    savings = Savings.objects.filter(client=client_contribution.client, type=Savings.DC).first()
    savings_payments = SavingsPayment.objects.filter(savings=savings, transaction_type=SavingsPayment.DC)
    withdrawals = SavingsPayment.objects.filter(savings=savings, transaction_type=SavingsPayment.WITHDRAWAL)

    monthly_totals = {}
    brought_forward = 0

    for payment in savings_payments:
        month = payment.payment_date.strftime('%Y-%m')
        if month not in monthly_totals:
            monthly_totals[month] = {'savings': 0, 'withdrawals': 0, 'brought_forward': brought_forward}
        monthly_totals[month]['savings'] += payment.amount

    for withdrawal in withdrawals:
        month = withdrawal.payment_date.strftime('%Y-%m')
        if month not in monthly_totals:
            monthly_totals[month] = {'savings': 0, 'withdrawals': 0, 'brought_forward': brought_forward}
        monthly_totals[month]['withdrawals'] += withdrawal.amount

    # Calculate brought forward for each month
    for month in sorted(monthly_totals.keys()):
        monthly_totals[month]['brought_forward'] = brought_forward
        brought_forward += monthly_totals[month]['savings'] - monthly_totals[month]['withdrawals']

    return monthly_totals

def daily_contribution_report(request):
    form = DCForm()
    events = []
    monthly_totals = {}

    if request.method == 'POST':
        form = DCForm(request.POST)
        if form.is_valid():
            dc_client = form.cleaned_data['client']
            client_contribution = ClientContribution.objects.get(id=dc_client.id)
            daily_contributions = DailyContribution.objects.filter(client_contribution=client_contribution)
            for contribution in daily_contributions:
                if contribution.payment_made:
                    events.append({
                        'title': '✓ ' + str(contribution.client_contribution.amount),
                        'start': contribution.date.isoformat(),
                        'classNames': 'tick'
                    })
                elif contribution.date < datetime.date.today():
                    events.append({
                        'title': '✗ ' + str(contribution.client_contribution.amount),
                        'start': contribution.date.isoformat(),
                        'classNames': 'cross'
                    })
                else:
                    events.append({
                        'title': str(contribution.client_contribution.amount),
                        'start': contribution.date.isoformat(),
                        'classNames': 'pending'
                    })
            monthly_totals = calculate_monthly_totals(dc_client)
            context = {
                'form': form,
                'events': events,
                'monthly_totals': monthly_totals
            }
            return render(request, 'test.html', context)
    else:
        form = DCForm()
    context = {
        'form': form,
        'events': events,
        'monthly_totals': monthly_totals
    }
    return render(request, 'test.html', context)


@login_required
def daily_contribution_spreadsheet(request):
    if request.method == 'POST':
        form = MonthYearForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
    else:
        form = MonthYearForm()
        month = datetime.date.today().month
        year = datetime.date.today().year

    clients = ClientContribution.objects.values_list('client','id', 'client__name', 'client__phone', 'amount')
    days_in_month = (datetime.date(year, month, 28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    days = [datetime.date(year, month, day).strftime('%Y-%m-%d') for day in range(1, days_in_month.day + 1)]
    
    contributions = {client_name: {'phone': phone, 'amount': amount, 'balance': 0, 'days': {day: False for day in days}} for client,client_id, client_name, phone, amount in clients}
    daily_contributions = DailyContribution.objects.filter(
        client_contribution__in=[client_id for _,client_id, _, _, _ in clients],
        date__month=month,
        date__year=year
    ).values_list('client_contribution__client__name', 'date', 'payment_made')

    for client,client_id, client_name, phone, amount in clients:
        savings = Savings.objects.filter(client=client, type=Savings.DC).first()
        if savings:
            contributions[client_name]['balance'] = savings.balance

    for client_name, date, payment_made in daily_contributions:
        if payment_made:
            contributions[client_name]['days'][date.strftime('%Y-%m-%d')] = True

    context = {
        'form': form,
        'days': days,
        'contributions': contributions
    }
    return render(request, 'daily_contribution_spreadsheet.html', context)


@login_required
def daily_contribution_spreadsheet_form(request):
    today = datetime.date.today()
    if request.method == 'POST':
        form = DailyContributionSpreadsheetForm(request.POST)
        if form.is_valid():
            contributions_data = form.cleaned_data['contributions']
            contributions = json.loads(contributions_data)

            with transaction.atomic():
                for client_id, payment_made in contributions.items():
                    if not payment_made:
                        continue
                    client_contribution = ClientContribution.objects.get(id=client_id)
                    try:
                        daily_contribution = DailyContribution.objects.get(
                            client_contribution=client_contribution,
                            date=today
                        )
                    except DailyContribution.DoesNotExist:
                        setup_monthly_contributions(client_contribution, today.month, today.year, request.user)
                        continue  
                    
                    daily_contribution.payment_made = payment_made
                    daily_contribution.save()
                    if payment_made:
                        create_dc_payment(daily_contribution, request)
                verify_trial_balance()
            return redirect('daily_contribution_spreadsheet')
    else:
        form = DailyContributionSpreadsheetForm()

    clients = ClientContribution.objects.values_list('id', 'client__name', 'client__phone', 'amount')
    contributions = {client_id: {'name': client_name, 'phone': phone, 'amount': amount, 'payment_made': False} for client_id, client_name, phone, amount in clients}
    daily_contributions = DailyContribution.objects.filter(
        client_contribution__in=[client_id for client_id, _, _, _ in clients],
        date=today
    ).values_list('client_contribution__id', 'payment_made')

    for client_id, payment_made in daily_contributions:
        contributions[client_id]['payment_made'] = payment_made

    context = {
        'form': form,
        'today': today,
        'contributions': contributions
    }
    return render(request, 'daily_contribution_spreadsheet_form.html', context)