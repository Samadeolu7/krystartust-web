import os
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from client.excel_utils import create_clients_from_excel
from client.models import Client
from loan.models import Loan, LoanPayment
from savings.models import Savings, SavingsPayment
from savings.utils import register_savings
from income.utils import create_income_payment, get_id_fee_income, get_registration_fee_income
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ClientExcelForm, ClientForm

# Create your views here.

def create_client(request):
    """View to handle creating a new client."""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client created successfully.')
            register_savings(client=form.instance, amount=form.cleaned_data["compulsory_savings"] )
            income = get_registration_fee_income()
            id_fee = get_id_fee_income()
            create_income_payment(bank=form.cleaned_data['bank'], income=income, description='Registration Fee', amount=form.cleaned_data['registration_fee'], payment_date=form.instance.created_at)
            create_income_payment(bank=form.cleaned_data['bank'], income=id_fee, description='ID Fee', amount=form.cleaned_data['id_fee'], payment_date=form.instance.created_at)
            
            
            return redirect('list_clients')  # Redirect to a client list or relevant page
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
            return redirect('individual_report', pk=client.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'client_form.html', {'form': form})


def list_clients(request):
    """View to list paginated and optimized clients."""
    
    # Number of clients per page
    clients_per_page = 20  # You can adjust this number as needed

    # Use select_related to fetch 'group' and prefetch_related for 'savings_set' and 'loan_set'
    clients_queryset = Client.objects.select_related('group').prefetch_related('savings_set', 'loan_set').order_by('id')

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
    }
    return render(request, 'client_list.html', context)


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


def create_client_excel(request):
    """View to create clients from an excel file."""
    if request.method == 'POST':
        form = ClientExcelForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['excel_file']
            report_path = create_clients_from_excel(file)

            # Create a CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_path)}"'

            with open(report_path, 'r') as report_file:
                response.write(report_file.read())

            messages.success(request, 'Clients created successfully. Check the report for more details.')
            return response
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = ClientExcelForm()
    
    return render(request, 'client_excel_form.html', {'form': form})