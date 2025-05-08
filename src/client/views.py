from decimal import Decimal
import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now
from administration.models import Transaction
from bank.utils import get_cash_in_hand
from client.excel_utils import create_clients_from_excel
from client.models import Client, Prospect, generate_client_id
from loan.models import Loan, LoanPayment
from main.utils import verify_trial_balance
from savings.models import Savings, SavingsPayment
from savings.utils import register_savings
from income.utils import create_income_payment, get_id_fee_income, get_registration_fee_income
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ClientForm, ProspectForm
from django.contrib.auth.decorators import login_required
from django.db import transaction

from administration.decorators import admin_required, allowed_users
# Create your views here.

@login_required
def create_client(request):
    """View to handle creating a new client."""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                client = form.save(commit=False)
                client.created_at = now().date()
                form.save()
                messages.success(request, 'Client created successfully.')
                bank = form.cleaned_data['bank']
                date = form.cleaned_data['date']
                tran = Transaction(description=f'Client Registration for {client.name}')
                tran.save(prefix='REG')
                register_savings(bank,client=form.instance, amount=form.cleaned_data["compulsory_savings"],date=date,transaction=tran,user=request.user)
                income = get_registration_fee_income()
                id_fee = get_id_fee_income()
                bank = form.cleaned_data['bank']
                create_income_payment(bank, income=income, description='Registration Fee', amount=form.cleaned_data['registration_fee'], payment_date=date, transaction=tran, user=request.user)
                create_income_payment(bank, income=id_fee, description='ID Fee', amount=form.cleaned_data['id_fee'], payment_date=date, transaction=tran, user=request.user)

                verify_trial_balance()
                
            
            return redirect('list_clients')  # Redirect to a client list or relevant page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm()
    
    return render(request, 'client_form.html', {'form': form})

@login_required
def edit_prospect(request, client_id):
    """View to handle editing an existing client."""
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        with transaction.atomic():
            if form.is_valid():
                form.save()
                messages.success(request, 'Client created successfully.')
                bank = form.cleaned_data['bank']
                date = form.cleaned_data['date']
                tran = Transaction(description=f'Client Registration for {client.name}')
                tran.save(prefix='REG')
                register_savings(bank,client=form.instance, amount=form.cleaned_data["compulsory_savings"],date=date,transaction=tran,user=request.user)
                income = get_registration_fee_income()
                id_fee = get_id_fee_income()
                bank = form.cleaned_data['bank']
                create_income_payment(bank, income=income, description='Registration Fee', amount=form.cleaned_data['registration_fee'], payment_date=date, transaction=tran, user=request.user)
                create_income_payment(bank, income=id_fee, description='ID Fee', amount=form.cleaned_data['id_fee'], payment_date=date, transaction=tran, user=request.user)

                verify_trial_balance()
                return redirect('individual_report', pk=client.id)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'client_form.html', {'form': form})

@login_required
def edit_client(request, client_id):
    """View to handle editing an existing client."""
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully.')
            return redirect('individual_report', pk=client.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'client_form.html', {'form': form})

from django.db.models import Q


@login_required
def list_clients(request):
    """View to list paginated and optimized clients based on search query."""
    
    # Number of clients per page
    clients_per_page = 20  # You can adjust this number as needed

    # Get the search query
    query = request.GET.get('q')

    # Initialize an empty queryset
    clients_queryset = Client.objects.none()
    if query:
        # Use select_related to fetch 'group' and prefetch_related for 'savings_set' and 'loan_set'
        clients_queryset = Client.objects.select_related('group').prefetch_related('savings_set', 'loans').filter(
            Q(name__icontains=query) | Q(client_id__icontains=query)
        ).order_by('id')

        # Initialize Paginator
        paginator = Paginator(clients_queryset, clients_per_page)
        page = request.GET.get('page')

        try:
            clients = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            clients = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver the last page of results.
            clients = paginator.page(paginator.num_pages)

        context = {
            'clients': clients,  # This is now a Page object
            'query': query,
        }
    else:
        context = {
            'clients': None,
            'query': query,
        }

    return render(request, 'client_list.html', context)


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def individual_report(request, pk):
    client = Client.objects.get(pk=pk)
    loans = Loan.objects.filter(client=client)
    savings = Savings.objects.filter(client=client)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    for loan in loans:
        loan.interest_amount = Decimal(loan.interest) * Decimal(loan.amount) / Decimal(100)
        
    loan_interest_amount= sum([loan.interest_amount for loan in loans])
    context = {
        'client': client,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
        'loan_interest_amount': loan_interest_amount,
    }

    return render(request, 'individual_report.html', context)

@login_required
def generate_client_id_view(request):
    client_type = request.GET.get('client_type')
    client_id = generate_client_id(client_type)
    return JsonResponse({'client_id': client_id})


@login_required
def create_prospect(request):
    """View to handle creating a new prospect."""
    if request.method == 'POST':
        form = ProspectForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.success(request, 'Prospect added successfully.')
            return redirect('list_clients')  # Redirect to the client list or relevant page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProspectForm()

    return render(request, 'prospect_form.html', {'form': form})
@login_required
def view_prospects(request):
    """View to list all prospects sorted by loan amount in ascending order."""
    prospects = Prospect.objects.filter(is_activated=False).order_by('loan_amount')  # Sort by loan amount (ascending)
    paginator = Paginator(prospects, 20)  # Paginate with 20 prospects per page
    page = request.GET.get('page')
    try:
        prospects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        prospects = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page of results.
        prospects = paginator.page(paginator.num_pages)
    context = {
        'prospects': prospects,
    }
    return render(request, 'prospect_list.html', context)