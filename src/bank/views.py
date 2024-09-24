from django.shortcuts import render
from .forms import BankForm, BankPaymentForm
from .models import Bank
from django.contrib.auth.decorators import login_required
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
