from django.shortcuts import redirect, render

from .forms import RegistrationFeeForm, IDFeeForm, LoanRegistrationFeeForm, RiskPremiumForm, UnionContributionForm, LoanServiceFeeForm

# Create your views here.

def set_fees(request):
    return render(request, 'set_fees.html')

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

