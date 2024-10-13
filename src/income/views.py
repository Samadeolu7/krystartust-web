from django.shortcuts import redirect, render

from .forms import RegistrationFeeForm, IDFeeForm, LoanRegistrationFeeForm, RiskPremiumForm, UnionContributionForm, LoanServiceFeeForm
from .models import Income, IncomePayment
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def income_list(request):
    incomes = Income.objects.all()
    return render(request, 'income_list.html', {'incomes': incomes})

@login_required
def income_details(request, pk):
    income = Income.objects.get(pk=pk)
    income_payment = IncomePayment.objects.filter(income_id=pk)

    context = {
        'income': income,
        'income_payment': income_payment
    }
    return render(request, 'income_details.html', context)

@login_required
def set_fees(request):
    return render(request, 'set_fees.html')

@login_required
def registration_fee(request):
    if request.method == 'POST':
        form = RegistrationFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = RegistrationFeeForm()
        title = 'Registration Fee'
        return render(request, 'fees.html', {'form': form,'title': title})

@login_required
def id_fee(request):
    if request.method == 'POST':
        form = IDFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = IDFeeForm()
        title = 'ID Fee'
        return render(request, 'fees.html', {'form': form,'title': title})

@login_required
def loan_registration_fee(request):
    if request.method == 'POST':
        form = LoanRegistrationFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = LoanRegistrationFeeForm()
        title = 'Loan Registration Fee'
        return render(request, 'fees.html', {'form': form,'title': title})

@login_required
def risk_premium(request):
    if request.method == 'POST':
        form = RiskPremiumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = RiskPremiumForm()
        title = 'Risk Premium'
        return render(request, 'fees.html', {'form': form,'title': title})

@login_required
def union_contribution(request):
    if request.method == 'POST':
        form = UnionContributionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = UnionContributionForm()
        title = 'Union Contribution'
        return render(request, 'fees.html', {'form': form,'title': title})

@login_required
def loan_service_fee(request):
    if request.method == 'POST':
        form = LoanServiceFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        
    else:
        form = LoanServiceFeeForm()
        title = 'Loan Service Fee'
        return render(request, 'fees.html', {'form': form,'title': title})

