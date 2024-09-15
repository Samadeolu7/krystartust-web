from django.shortcuts import redirect, render

from loan.models import Loan, LoanPayment
from savings.models import Savings, SavingsPayment

from .models import ClientGroup as Group
from .forms import GroupForm
from client.models import Client
# Create your views here.

def dashboard(request):
    """View to render the main dashboard."""
    return render(request, 'dashboard.html')

def group_detail(request, pk):
    group = Client.objects.get(group=pk)
    return render(request, 'group_detail.html', {'group': group})

def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_view')
    else:
        form = GroupForm()
    
    return render(request, 'group_form.html', {'form': form})

def group_view(request):
    groups = Group.objects.all()
    return render(request, 'group_view.html', {'groups': groups})

def group_edit(request, pk):
    group = Group.objects.get(pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'group_form.html', {'form': form})

def group_report(request, pk):
    group = Group.objects.get(pk=pk)
    clients = Client.objects.filter(group=group)
    loans = Loan.objects.filter(client__in=clients)
    savings = Savings.objects.filter(client__in=clients)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'group': group,
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'group_report.html', context)