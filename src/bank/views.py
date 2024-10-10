from datetime import datetime, timezone
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import BankForm, BankPaymentForm, CashTransferForm
from .models import Bank, BankPayment
from django.contrib.auth.decorators import login_required

from .excel_utils import bank_to_excel
# Create your views here.

@login_required
def create_bank(request):
    form = BankForm()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_bank.html', {'form': form})

@login_required
def create_bank_payment(request):
    form = BankPaymentForm()
    if request.method == 'POST':
        form = BankPaymentForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_bank_payment.html', {'form': form})

@login_required
def bank_list(request):
    bank = Bank.objects.all()
    return render(request, 'bank_list.html', {'bank': bank})

@login_required
def bank_detail(request, pk):
    bank = Bank.objects.get(pk=pk)
    bank_payment = bank.bankpayment_set.all()
    context = {
        'bank': bank,
        'bank_payment': bank_payment
    }
    return render(request, 'bank_detail.html', context)

# views.py


def cash_transfer(request):
    if request.method == 'POST':
        form = CashTransferForm(request.POST)
        if form.is_valid():
            source_bank = form.cleaned_data['source_bank']
            destination_bank = form.cleaned_data['destination_bank']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            # Create BankPayment for source bank (debit)
            
            BankPayment.objects.create(
                bank=source_bank,
                description=f"Transfer to {destination_bank.name}: {description}",
                amount=-amount,
                bank_balance=source_bank.balance - amount,
                payment_date=form.cleaned_data['payment_date']
            )

            # Create BankPayment for destination bank (credit)
            BankPayment.objects.create(
                bank=destination_bank,
                description=f"Transfer from {source_bank.name}: {description}",
                amount=amount,
                bank_balance=destination_bank.balance + amount,
                payment_date=form.cleaned_data['payment_date']
            )

            return redirect('dashboard')
    else:
        form = CashTransferForm()
        form.fields['payment_date'].initial = datetime.now().date()

    return render(request, 'cash_transfer.html', {'form': form})

@login_required
def bank_to_excel_view(request, pk):
    bank = Bank.objects.get(pk=pk)
    df = bank_to_excel(bank)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename={bank.name}_payments.xlsx'
    df.to_excel(response, index=False)
    return response