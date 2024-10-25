from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render

from administration.decorators import allowed_users
from administration.models import Approval, Transaction
from main.utils import verify_trial_balance
from .models import Savings, SavingsPayment
from .forms import SavingsForm, WithdrawalForm, CompulsorySavingsForm, SavingsExcelForm, CombinedPaymentForm
from .excel_utils import savings_from_excel
from bank.utils import create_bank_payment
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType


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
@allowed_users(allowed_roles=['Admin', 'Manager'])
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
                    payment_date=form.cleaned_data['payment_date'],
                    transaction=loan.transaction,
                    created_by=request.user
                )
                create_bank_payment(
                    bank=bank,
                    description=f"Savings Payment by {savings.client.name}",
                    amount=savings.amount,
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
@allowed_users(allowed_roles=['Admin', 'Manager'])
def record_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                if form.cleaned_data['amount'] > form.cleaned_data['savings'].balance:
                    messages.error(request, 'Insufficient balance')
                    return redirect('savings_withdrawal')
                
                withdrawal = form.save(commit=False)
                tran = Transaction(description=f'Withdrawal for {withdrawal.savings.client.name}')
                tran.save(prefix='WDL')
                withdrawal.transaction = tran
                withdrawal.save()  # Ensure the object is saved before checking its ID
                if withdrawal.id is None:
                    return redirect('savings_withdrawal')

                withdrawal.save()

                approval = Approval.objects.create(
                    type=Approval.Withdrawal,
                    content_object=withdrawal,
                    content_type=ContentType.objects.get_for_model(SavingsPayment),
                    user=request.user,
                    object_id=withdrawal.id
                )
                
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