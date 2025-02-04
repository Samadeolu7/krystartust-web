from django.shortcuts import redirect, render

from main.models import Year

from .forms import RegistrationFeeForm, IDFeeForm, LoanRegistrationFeeForm, RiskPremiumForm, UnionContributionForm, LoanServiceFeeForm
from .models import Income, IncomePayment
from django.contrib.auth.decorators import login_required
from administration.decorators import allowed_users
# Create your views here.


@login_required
@allowed_users(allowed_roles=['Admin'])
def income_list(request):
    current_year = Year.current_year()
    incomes = Income.objects.filter(year=current_year)
    has_previous_income = Income.objects.filter(year__lt=current_year).exists()

    context={
        'incomes': incomes,
        'has_previous_income': has_previous_income
    }
    return render(request, 'income_list.html', context)

@login_required
@allowed_users(allowed_roles=['Admin'])



@login_required
@allowed_users(allowed_roles=['Admin'])
def income_details(request, pk):
    income = Income.objects.get(pk=pk)
    income_payment = IncomePayment.objects.filter(income_id=pk)

    context = {
        'income': income,
        'income_payment': income_payment
    }
    return render(request, 'income_details.html', context)


@login_required
@allowed_users(allowed_roles=['Admin'])
def set_fees(request):
    return render(request, 'set_fees.html')


@login_required
@allowed_users(allowed_roles=['Admin'])
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
@allowed_users(allowed_roles=['Admin'])
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
@allowed_users(allowed_roles=['Admin'])
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
@allowed_users(allowed_roles=['Admin'])
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
@allowed_users(allowed_roles=['Admin'])
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
@allowed_users(allowed_roles=['Admin'])
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