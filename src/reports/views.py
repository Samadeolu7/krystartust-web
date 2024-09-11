from django.shortcuts import render

from client.models import Client
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from savings.models import Savings, SavingsPayment
from main.models import ClientGroup as Group

# Create your views here.

def all_clients_report(request):
    clients = Client.objects.all()
    loans = Loan.objects.filter(client__in=clients)
    savings = Savings.objects.filter(client__in=clients)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'all_clients_report.html', context)

def all_groups_report(request):
    groups = Group.objects.all()
    clients = Client.objects.filter(group__in=groups)
    loans = Loan.objects.filter(client__in=clients)
    savings = Savings.objects.filter(client__in=clients)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'groups': groups,
        'clients': clients,
        'loans': loans,
        'savings': savings,
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
    }

    return render(request, 'all_groups_report.html', context)

def all_loans_report(request):
    loans = Loan.objects.all()
    clients = Client.objects.filter(loan__in=loans)
    loan_payments = LoanPayment.objects.filter(loan__in=loans)
    context = {
        'loans': loans,
        'clients': clients,
        'loan_payments': loan_payments,
    }

    return render(request, 'all_loans_report.html', context)

def all_savings_report(request):
    savings = Savings.objects.all()
    clients = Client.objects.filter(savings__in=savings)
    savings_payments = SavingsPayment.objects.filter(savings__in=savings)
    context = {
        'savings': savings,
        'clients': clients,
        'savings_payments': savings_payments,
    }

    return render(request, 'all_savings_report.html', context)

def all_transactions_report(request):
    loan_payments = LoanPayment.objects.all()
    savings_payments = SavingsPayment.objects.all()
    loans = Loan.objects.filter(loan_payment__in=loan_payments)
    savings = Savings.objects.filter(savings_payment__in=savings_payments)
    clients = Client.objects.filter(loan__in=loans, savings__in=savings)
    context = {
        'loan_payments': loan_payments,
        'savings_payments': savings_payments,
        'loans': loans,
        'savings': savings,
        'clients': clients,
    }
    
    return render(request, 'all_transactions_report.html', context)

def daily_collection_form(request):
    return render(request, 'daily_collection_form.html')

def daily_transactions_report(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        schedule = LoanRepaymentSchedule.objects.filter(due_date=date)
        loan_payments = LoanPayment.objects.filter(payment_date=date)
        savings_payments = SavingsPayment.objects.filter(payment_date=date)
        loans = Loan.objects.filter(loan_payment__in=loan_payments)
        savings = Savings.objects.filter(savings_payment__in=savings_payments)
        clients = Client.objects.filter(loan__in=loans, savings__in=savings)
        context = {
            'Schedule': schedule,
            'loan_payments': loan_payments,
            'savings_payments': savings_payments,
            'loans': loans,
            'savings': savings,
            'clients': clients,
        }
    else:
        return render(request, 'daily_collection_form.html')
    return render(request, 'daily_transactions_report.html', context)