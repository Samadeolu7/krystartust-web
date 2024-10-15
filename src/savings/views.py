from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render

from main.utils import verify_trial_balance
from .models import Savings, SavingsPayment
from .forms import SavingsForm, WithdrawalForm, CompulsorySavingsForm, SavingsExcelForm, CombinedPaymentForm
from .excel_utils import savings_from_excel
from bank.utils import create_bank_payment, get_cash_in_hand
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages


@login_required
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
    savings = Savings.objects.get(client_id=client_id)
    savings_payments = SavingsPayment.objects.filter(client_id=client_id)
    context = {
        'savings': savings,
        'savings_payments': savings_payments
    }
    return render(request, 'savings_detail.html', context)

@login_required
def register_savings(request):
    if request.method == 'POST':
        form = SavingsForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                savings = form.save()
                create_bank_payment(
                    bank=form.cleaned_data['bank'],
                    description=f"Savings Payment by {savings.client.name}",
                    amount=form.cleaned_data['amount'],
                    payment_date=form.cleaned_data['payment_date']
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
def register_payment(request):
    if request.method == 'POST':
        form = CombinedPaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                loan,savings = form.save()
                bank = form.cleaned_data['bank']
                create_bank_payment(
                    bank=bank,
                    description=form.cleaned_data['description'],
                    amount=loan.amount,
                    payment_date=form.cleaned_data['payment_date']
                )
                create_bank_payment(
                    bank=bank,
                    description=f"Savings Payment by {savings.client.name}",
                    amount=savings.amount,
                    payment_date=form.cleaned_data['payment_date']
                )
                verify_trial_balance()
            
            return redirect('dashboard')
    else:
        form = CombinedPaymentForm()
    return render(request, 'combined_payment_form.html', {'form': form})


@login_required
def record_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('dashboard')
    else:
        form = WithdrawalForm()
    return render(request, 'withdrawal_form.html', {'form': form})

@login_required
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