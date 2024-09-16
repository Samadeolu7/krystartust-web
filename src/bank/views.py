from django.shortcuts import render
from .forms import BankForm, BankPaymentForm
from .models import Bank

# Create your views here.

def create_bank(request):
    form = BankForm()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_bank.html', {'form': form})

def create_bank_payment(request):
    form = BankPaymentForm()
    if request.method == 'POST':
        form = BankPaymentForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_bank_payment.html', {'form': form})

def bank_list(request):
    bank = Bank.objects.all()
    return render(request, 'bank_list.html', {'bank': bank})

def bank_detail(request, pk):
    bank = Bank.objects.get(pk=pk)
    return render(request, 'bank_detail.html', {'bank': bank})
