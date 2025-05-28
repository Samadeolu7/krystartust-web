from gettext import translation
from django.shortcuts import render

# Create your views here.

from datetime import datetime, timezone
from django.shortcuts import redirect, render
from django.db import transaction
from administration.decorators import allowed_users

from administration.models import Transaction
from administration.utils import validate_month_status
from main.models import Year
from main.utils import verify_trial_balance
from .forms import LiabilityForm, LiabilityPaymentForm
from .models import Liability, LiabilityPayment
from django.contrib.auth.decorators import login_required
from bank.utils import create_bank_payment, get_bank_account
# Create your views here.


@login_required
@allowed_users(allowed_roles=['Admin'])
def create_liability(request):
    form = LiabilityForm()
    if request.method == 'POST':
        form = LiabilityForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                verify_trial_balance()
                return redirect('liability_list')

    return render(request, 'create_liability.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def liability_payment(request):
    form = LiabilityPaymentForm()
    if request.method == 'POST':
        form = LiabilityPaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                liability = form.save(commit=False)
                try:
                    validate_month_status(liability.payment_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'liability_payment.html', {'form': form})
                tran = Transaction(description=f'liability payment for {form.cleaned_data["liability"]}')
                tran.save(prefix='LIA')
                liability.created_by = request.user
                liability.transaction = tran
                bank = get_bank_account()
                amount = form.cleaned_data['amount'] * -1
                
                create_bank_payment(bank,f'liability payment for {form.cleaned_data["liability"]}', amount, form.cleaned_data['payment_date'], tran, request.user)
                verify_trial_balance()
            return redirect('dashboard')
    return render(request, 'create_liability_payment.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def liability_list(request):
    year = Year.current_year()
    liability = Liability.objects.filter(year=year).all()
    has_previous_liability = Liability.objects.filter(year__lt=year).exists()

    context = {
        'liability': liability,
        'has_previous_liability': has_previous_liability
    }
    return render(request, 'liability_list.html', context)


@login_required
@allowed_users(allowed_roles=['Admin'])
def liability_detail(request, pk):
    liability = Liability.objects.get(pk=pk)
    liability_payment = LiabilityPayment.objects.filter(liability=liability).all()
    context = {
        'liability': liability,
        'liability_payment': liability_payment
    }
    return render(request, 'liability_detail.html', context)

# views.py
