from django.shortcuts import render

# Create your views here.

from datetime import datetime, timezone
from django.shortcuts import redirect, render
from .forms import LiabilityForm, LiabilityPaymentForm
from .models import Liability, LiabilityPayment
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def create_liability(request):
    form = LiabilityForm()
    if request.method == 'POST':
        form = LiabilityForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_liability.html', {'form': form})

@login_required
def liability_payment(request):
    form = LiabilityPaymentForm()
    if request.method == 'POST':
        form = LiabilityPaymentForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_liability_payment.html', {'form': form})

@login_required
def liability_list(request):
    liability = Liability.objects.all()
    return render(request, 'liability_list.html', {'liability': liability})

@login_required
def liability_detail(request, pk):
    liability = Liability.objects.get(pk=pk)
    liability_payment = liability.liability_payments.all()
    context = {
        'liability': liability,
        'liability_payment': liability_payment
    }
    return render(request, 'liability_detail.html', context)

# views.py
