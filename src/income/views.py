from django.shortcuts import render

from .forms import RegistrationFeeForm, IDFeeForm, LoanRegistrationFeeForm, RiskPremiumForm, UnionContributionForm, LoanServiceFeeForm

# Create your views here.

def set_fees(request):
    return render(request, 'set_fees.html')

def registration_fee(request):
    if request.method == 'POST':
        form = RegistrationFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'fees.html', {'form': form})
        
    else:
        form = RegistrationFeeForm()
        return render(request, 'fees.html', {'form': form})

def id_fee(request):
    if request.method == 'POST':
        form = IDFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'fees.html', {'form': form})
        
    else:
        form = IDFeeForm()
        return render(request, 'fees.html', {'form': form})

def loan_registration_fee(request):
    if request.method == 'POST':
        form = LoanRegistrationFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'fees.html', {'form': form})
        
    else:
        form = LoanRegistrationFeeForm()
        return render(request, 'fees.html', {'form': form})

def risk_premium(request):
    if request.method == 'POST':
        form = RiskPremiumForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'fees.html', {'form': form})
        
    else:
        form = RiskPremiumForm()
        return render(request, 'fees.html', {'form': form})

def union_contribution(request):
    if request.method == 'POST':
        form = UnionContributionForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'fees.html', {'form': form})
        
    else:
        form = UnionContributionForm()
        return render(request, 'fees.html', {'form': form})

def loan_service_fee(request):
    if request.method == 'POST':
        form = LoanServiceFeeForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'fees.html', {'form': form})
        
    else:
        form = LoanServiceFeeForm()
        return render(request, 'fees.html', {'form': form})

