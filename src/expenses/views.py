from datetime import datetime, timezone
from django.shortcuts import redirect, render
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from administration.utils import validate_month_status
from main.utils import verify_trial_balance
from .forms import ExpenseForm, ExpensePaymentBatchForm, ExpensePaymentForm, ExpenseTypeForm, ExpensePaymentBatchItemFormSet
from .models import Expense, ExpensePayment, ExpensePaymentBatch, ExpenseType
from django.contrib.auth.decorators import login_required
from django.db import transaction
from administration.decorators import allowed_users
from administration.models import Transaction , Approval
from bank.utils import create_bank_payment, get_bank_account
# Create your views here.


@login_required
@allowed_users(allowed_roles=['Admin'])
def create_expense(request):
    form = ExpenseForm()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_expense.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
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
            with transaction.atomic():
                expense =form.save(commit=False)
                try:
                    validate_month_status(expense.payment_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'expense_payment.html', {'form': form})
                tran = Transaction(description=f'expense for {form.cleaned_data["expense"]}')
                tran.save(prefix='EXP') 
                expense.created_by = request.user
                expense.transaction = tran
                expense.balance = expense.expense.balance
                expense.save()

                approval = Approval.objects.create(
                    type=Approval.Expenses,
                    content_object=expense,
                    content_type=ContentType.objects.get_for_model(Expense),
                    user=request.user,
                    object_id=expense.id
                )
                messages.success(request, 'Expense Request sent for approval')

                verify_trial_balance()
            return redirect('dashboard')
                
    return render(request, 'expense_payment.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def expense_list(request):
    expense = Expense.objects.all()
    return render(request, 'expense_list.html', {'expense': expense})


@login_required
@allowed_users(allowed_roles=['Admin'])
def expense_detail(request, pk):
    expense = Expense.objects.get(pk=pk)
    
    expense_payment = ExpensePayment.objects.filter(expense=expense).all()
    context = {
        'expense': expense,
        'expense_payment': expense_payment
    }
    return render(request, 'expense_detail.html', context)

def create_expense_payment_batch(request):
    if request.method == 'POST':
        batch_form = ExpensePaymentBatchForm(request.POST)
        formset = ExpensePaymentBatchItemFormSet(request.POST)
        if batch_form.is_valid() and formset.is_valid():
            with transaction.atomic():

                batch = batch_form.save(commit=False)
                try:
                    validate_month_status(batch.payment_date)
                except Exception as e:
                    batch_form.add_error(None, e)
                    return render(request, 'test_batch.html', {
                        'batch_form': batch_form,
                        'formset': formset,
                    })
                batch.created_by = request.user
                batch.save()
                formset.instance = batch
                formset.save()
                Approval.objects.create(
                    type=Approval.Batch_Expense,
                    content_object=batch,
                    content_type=ContentType.objects.get_for_model(ExpensePaymentBatch),
                    user=request.user,
                    object_id=batch.id
                )
                verify_trial_balance()
                messages.success(request, 'Expense Payment Batch created successfully')
                
                return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        batch_form = ExpensePaymentBatchForm()
        formset = ExpensePaymentBatchItemFormSet()

    return render(request, 'create_expense_payment_batch.html', {
        'batch_form': batch_form,
        'formset': formset,
    })