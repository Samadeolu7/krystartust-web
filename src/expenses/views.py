from datetime import datetime, timezone
from django.shortcuts import redirect, render
from .forms import ExpenseForm, ExpensePaymentForm, ExpenseTypeForm
from .models import Expense, ExpensePayment, ExpenseType
from django.contrib.auth.decorators import login_required

from bank.utils import create_bank_payment, get_bank_account
# Create your views here.

@login_required
def create_expense(request):
    form = ExpenseForm()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_expense.html', {'form': form})

@login_required
def create_expense_type(request):
    form = ExpenseTypeForm()
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_expense_type.html', {'form': form})

@login_required
def expense_payment(request):
    form = ExpensePaymentForm()
    if request.method == 'POST':
        form = ExpensePaymentForm(request.POST)
        if form.is_valid():
            form.save()
            bank = get_bank_account()
            amount = form.cleaned_data['amount'] * -1
            create_bank_payment(bank,f'expense for {form.cleaned_data["expense"]}', amount, form.cleaned_data['payment_date'])
            
    return render(request, 'expense_payment.html', {'form': form})

@login_required
def expense_list(request):
    expense = Expense.objects.all()
    return render(request, 'expense_list.html', {'expense': expense})

@login_required
def expense_detail(request, pk):
    expense = Expense.objects.get(pk=pk)
    
    expense_payment = ExpensePayment.objects.filter(expense=expense).all()
    context = {
        'expense': expense,
        'expense_payment': expense_payment
    }
    return render(request, 'expense_detail.html', context)

# views.py
