from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render
from .models import SavingsPayment
from .forms import SavingsForm, WithdrawalForm, CompulsorySavingsForm, SavingsExcelForm
from .excel_utils import savings_from_excel



def compulsory_savings(request):
    if request.method == 'POST':
        form = CompulsorySavingsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = CompulsorySavingsForm()
        title = 'Compulsory Savings'
        return render(request, 'fees.html', {'form': form,'title': title})

def transaction_history(request, client_id):
    transactions = SavingsPayment.objects.filter(client_id=client_id).order_by('-created_at')
    return render(request, 'transaction_history.html', {'transactions': transactions})

def register_savings(request):
    if request.method == 'POST':
        form = SavingsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SavingsForm()
    return render(request, 'savings_form.html', {'form': form})

def record_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = WithdrawalForm()
    return render(request, 'withdrawal_form.html', {'form': form})

def upload_savings(request):
    if request.method == 'POST':
        form = SavingsExcelForm(request.POST, request.FILES)
        if form.is_valid():
            report_path = savings_from_excel(request.FILES['excel_file'])

            # Read the report file content
            with open(report_path, 'r') as report_file:
                report_content = report_file.read()

            # Create a downloadable response
            response = HttpResponse(report_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="savings_report.csv"'
            return response
    else:
        form = SavingsExcelForm()
    return render(request, 'upload_savings.html', {'form': form})