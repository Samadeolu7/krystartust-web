from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from client.models import Client
from loan.models import Loan, LoanPayment
from savings.models import Savings, SavingsPayment
from savings.utils import register_savings
from income.utils import create_income_payment, get_id_fee_income, get_registration_fee_income

from .forms import ClientForm

# Create your views here.

def create_client(request):
    """View to handle creating a new client."""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client created successfully.')
            register_savings(client=form.instance, amount=form.cleaned_data["compulsory_savings"], bank=form.cleaned_data['bank'], created_by=request.user)
            income = get_registration_fee_income()
            id_fee = get_id_fee_income()
            create_income_payment(bank=form.cleaned_data['bank'], income=income, description='Registration Fee', amount=form.cleaned_data['registration_fee'], created_by=request.user, payment_date=form.instance.created_at)
            create_income_payment(bank=form.cleaned_data['bank'], income=id_fee, description='ID Fee', amount=form.cleaned_data['id_fee'], created_by=request.user, payment_date=form.instance.created_at)
            
            
            return redirect('client_list')  # Redirect to a client list or relevant page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm()
    
    return render(request, 'client_form.html', {'form': form})

def edit_client(request, client_id):
    """View to handle editing an existing client."""
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully.')
            return redirect('client_list')  # Redirect to a client list or relevant page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'client_form.html', {'form': form})

def list_clients(request):
    """View to list all clients."""
    clients = Client.objects.all()
    return render(request, 'client_list.html', {'clients': clients})


def individual_report(request, pk):
    client = Client.objects.get(pk=pk)
    loans = Loan.objects.filter(client=client)
    savings = Savings.objects.filter(client=client)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'client': client,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'individual_report.html', context)