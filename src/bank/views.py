from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from administration.models import Transaction
from administration.utils import validate_month_status
from .forms import BankForm, BankPaymentForm, CashTransferForm, DateRangeForm
from .models import Bank, BankPayment
from django.contrib.auth.decorators import login_required
from administration.decorators import allowed_users

from .excel_utils import bank_to_excel
# Create your views here.

@login_required
@allowed_users(allowed_roles=['Admin'])
def create_bank(request):
    form = BankForm()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_bank.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def create_bank_payment(request):
    form = BankPaymentForm()
    
    if request.method == 'POST':
        form = BankPaymentForm(request.POST)
        if form.is_valid():

            form.save()
    return render(request, 'create_bank_payment.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_list(request):
    bank = Bank.objects.all()
    return render(request, 'bank_list.html', {'bank': bank})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_detail(request, pk):
    bank = Bank.objects.get(pk=pk)
    today = timezone.now().date()
    start_date = today - timedelta(days=30)

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Ensure the date range does not exceed 2 months
            if (end_date - start_date).days > 60:
                form.add_error(None, 'Date range cannot exceed 2 months.')
                end_date = today
                start_date = today - timedelta(days=60)
        else:
            end_date = today
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': today})
        end_date = today

    bank_payment = bank.payments.filter(payment_date__range=[start_date, end_date])

    context = {
        'bank': bank,
        'bank_payment': bank_payment,
        'form': form,
    }
    return render(request, 'bank_detail.html', context)

# views.py

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def cash_transfer(request):
    if request.method == 'POST':
        form = CashTransferForm(request.POST)
        if form.is_valid():
            payment_date = form.cleaned_data['payment_date']
            try:
                validate_month_status(payment_date)
            except Exception as e:
                form.add_error(None, e)
                return render(request, 'cash_transfer.html', {'form': form})
            source_bank = form.cleaned_data['source_bank']
            destination_bank = form.cleaned_data['destination_bank']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            # Create BankPayment for source bank (debit)

            tran = Transaction(description=f'Transfer to {destination_bank.name}: {description}')
            
            BankPayment.objects.create(
                bank=source_bank,
                description=f"Transfer to {destination_bank.name}: {description}",
                amount=-amount,
                bank_balance=source_bank.balance - amount,
                payment_date=payment_date,
                transaction=tran
            )

            # Create BankPayment for destination bank (credit)
            BankPayment.objects.create(
                bank=destination_bank,
                description=f"Transfer from {source_bank.name}: {description}",
                amount=amount,
                bank_balance=destination_bank.balance + amount,
                payment_date=payment_date,
                transaction=tran
            )

            return redirect('dashboard')
    else:
        form = CashTransferForm()
        form.fields['payment_date'].initial = datetime.now().date()

    return render(request, 'cash_transfer.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_to_excel_view(request, pk):
    bank = Bank.objects.get(pk=pk)
    df = bank_to_excel(bank)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename={bank.name}_payments.xlsx'
    df.to_excel(response, index=False)
    return response