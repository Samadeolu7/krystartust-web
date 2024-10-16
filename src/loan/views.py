from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from client.models import Client
from income.models import IncomePayment
from liability.utils import create_union_contribution_income_payment
from loan.excel_utils import bulk_create_loans_from_excel, loan_from_excel
from savings.models import Savings, SavingsPayment
from bank.models import BankPayment
from main.models import ClientGroup as Group
from .models import Loan, LoanPayment, LoanRepaymentSchedule
from .forms import LoanRegistrationForm, LoanPaymentForm, LoanExcelForm, LoanUploadForm
from django.contrib.auth.decorators import login_required
from django.db import transaction

from bank.utils import create_bank_payment
from income.utils import create_risk_premium_income_payment, get_loan_interest_income, create_administrative_fee_income_payment, create_loan_registration_fee_income_payment
from main.utils import verify_trial_balance

from datetime import date, timedelta

# Create your views here.

@login_required
def transaction_history(request, client_id):
    transactions = Loan.objects.filter(client_id=client_id).order_by('-created_at')
    return render(request, 'transaction_history.html', {'transactions': transactions})

@login_required
def loan_payment(request):
    if request.method == 'POST':
        form = LoanPaymentForm(request.POST)
        if form.is_valid():
            # Save the loan payment record
            with transaction.atomic():
                loan_payment = form.save(commit=False)
                loan_id = loan_payment.loan.id
                
                # Retrieve and update the repayment schedule
                schedule = LoanRepaymentSchedule.objects.filter(id=loan_payment.payment_schedule.id).first()
                if schedule:
                    schedule.is_paid = True
                    schedule.save()
                else:
                    messages.error(request, "Payment schedule not found.")
                    return render(request, 'loan_payment_form.html', {'form': form})
                
                # Update the loan balance
                loan = Loan.objects.filter(id=loan_id).first()
                if loan:
                    loan.balance -= Decimal(loan_payment.amount)
                    loan.save()
                else:
                    messages.error(request, "Loan not found.")
                    return render(request, 'loan_payment_form.html', {'form': form})
                
                # Save the payment after modifying the balance and schedule
                # include client in the payment
                loan_payment.client = loan.client
                loan_payment.save()

                # Update the bank balance
                bank = form.cleaned_data.get('bank')
                create_bank_payment(bank, f'Loan payment from {loan.client.name}',loan_payment.amount, loan_payment.payment_date)

                verify_trial_balance()
                
                messages.success(request, "Loan payment processed successfully.")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")
    else:
        form = LoanPaymentForm()
    
    return render(request, 'loan_payment_form.html', {'form': form})

@login_required
def load_payment_schedules(request):
    loan_id = request.GET.get('loan_id')
    try:
        loan = Loan.objects.get(id=loan_id)
        payment_schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan.id, is_paid=False).order_by('due_date')
        return JsonResponse(list(payment_schedules.values('id', 'due_date', 'amount_due')), safe=False)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'Loan not found'}, status=404)
    
@login_required
def load_payment_schedules_com(request):
    client_id = request.GET.get('client_id')
    try:
        loan = Loan.objects.get(client_id=client_id)
        payment_schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan.id, is_paid=False).order_by('due_date')
        return JsonResponse(list(payment_schedules.values('id', 'due_date', 'amount_due')), safe=False)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'Loan not found'}, status=404)

@login_required
def loan_upload_view(request):
    if request.method == 'POST':
        form = LoanUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            report_path = bulk_create_loans_from_excel(file)

            # Read the report file content
            with open(report_path, 'r') as report_file:
                report_content = report_file.read()

            # Create a downloadable response
            response = HttpResponse(report_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="loan_creation_report.csv"'
            return response
        else:
            messages.error(request, "There was an error with the form. Please correct it below.")
    else:
        form = LoanUploadForm()

    return render(request, 'upload_loan.html', {'form': form})

@login_required
def loan_registration(request):
    if request.method == 'POST':
        form = LoanRegistrationForm(request.POST)
        if form.is_valid():
            # Save the loan form data to create a new Loan instance

            with transaction.atomic():
                loan = form.save(commit=False)
                loan.balance = loan.amount * (Decimal(1) + (Decimal(loan.interest)/Decimal(100)))
                loan.end_date = loan.start_date + timedelta(days=loan.duration) + timedelta(weeks=1)  # Extend end date by 1 week
                loan.emi = loan.balance / loan.duration
                loan.status = 'Active'
                loan.save()

                # Get the loan details
                loan_type = loan.loan_type
                duration = loan.duration
                start_date = loan.start_date
                amount = loan.amount
                registration_fee = form.cleaned_data.get('registration_fee')
                bank = form.cleaned_data.get('bank')
                admin_fees = form.cleaned_data.get('admin_fees')
                if admin_fees:
                    admin_fee_amount = Decimal(admin_fees) * Decimal(amount) / Decimal(100)
                    create_administrative_fee_income_payment(admin_fee_amount,start_date, f'Administrative Fee for {loan.client.name}')

                if registration_fee:
                    create_loan_registration_fee_income_payment(registration_fee,start_date, f'Loan Registration Fee for {loan.client.name}')

                # Determine the increment based on loan type
                time_increment = {
                    'Daily': timedelta(days=1),
                    'Weekly': timedelta(weeks=1),
                    'Monthly': timedelta(weeks=4),
                    # Add more loan types as needed
                }.get(loan_type, timedelta(weeks=1))  # Default to weekly if the loan type is not specifically listed

                # Create repayment schedule based on the loan type and duration
                amount_due = loan.balance / duration
                for i in range(duration):
                    due_date = start_date + timedelta(weeks=1) + (i * time_increment)  # Start 1 week after the start date

                    LoanRepaymentSchedule.objects.create(
                        loan=loan,
                        due_date=due_date,
                        amount_due=amount_due,
                    )

                # Subtract loan amount from bank balance
                bank_payment = BankPayment.objects.create(
                    bank=bank,
                    description=f'Loan disbursement to {loan.client.name}',
                    amount=-amount,
                    payment_date=start_date,
                )
                bank_payment.save()

                interest_amount = Decimal(loan.interest) * Decimal(amount) / Decimal(100)
                if loan_type == 'Daily':
                    interest_income = get_loan_interest_income(type='Daily')
                elif loan_type == 'Weekly':
                    interest_income = get_loan_interest_income(type='Weekly')
                else:
                    interest_income = get_loan_interest_income(type='Monthly')
                income_payment = IncomePayment.objects.create(
                    income=interest_income,
                    description=f'Interest income from {loan.client.name}',
                    amount=interest_amount,
                    payment_date=start_date,
                )
                income_payment.save()
                risk_premium_amount = Decimal(loan.risk_premium) * Decimal(amount) / 100
                create_risk_premium_income_payment(risk_premium_amount, start_date, f'Risk Premium for {loan.client.name}')

                union = form.cleaned_data.get('union_contribution')
                create_union_contribution_income_payment(start_date,union,f'Union Contribution for {loan.client.name}')

                verify_trial_balance()

            messages.success(request, "Loan registered successfully and repayment schedule created.")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error with the form. Please correct it below.")
    else:
        form = LoanRegistrationForm()

    return render(request, 'loan_register.html', {'form': form})

@login_required
def loan_detail(request, client_id):
    loan = Loan.objects.filter(client=client_id).first()
    loan_payments = LoanPayment.objects.filter(loan=loan)
    loan_interest_amount = Decimal(loan.interest) * Decimal(loan.amount) / Decimal(100)
    context = {
        'loan': loan,
        'loan_payments': loan_payments,
        'loan_interest_amount': loan_interest_amount,
    }
    return render(request, 'loan_detail.html', context)

@login_required
def loan_schedule(request, loan_id):
    schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_id).order_by('due_date')
    return render(request, 'loan_schedule.html', {'schedules': schedules})


@login_required
def loan_defaulters_report(request):
    today = date.today()

    # Fetch the necessary fields from the loan repayment schedule to avoid unnecessary data loading
    overdue_schedules = LoanRepaymentSchedule.objects.filter(
        due_date__lt=today,
        is_paid=False
    ).select_related('loan').only(
        'loan__id', 'loan__client__name', 'loan__client__phone', 'loan__amount', 'loan__balance', 
        'loan__start_date', 'loan__end_date', 'loan__status', 'due_date', 'amount_due', 'is_paid'
    )

    # Fetch the defaulters, filtering only by IDs and loading required fields
    defaulters = Loan.objects.filter(
        id__in=overdue_schedules.values('loan_id'),
        status='Active'
    ).only(
        'id', 'client__name', 'client__phone', 'amount', 'balance', 'start_date', 'end_date', 'status'
    ).distinct()

    context = {
        'defaulters': defaulters,
        'schedule': overdue_schedules,
    }

    return render(request, 'loan_defaulters_report.html', context)


@login_required
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


@login_required
def loan_upload(request):
    if request.method == 'POST':
        form = LoanExcelForm(request.POST, request.FILES)
        if form.is_valid():
            report_content = loan_from_excel(request.FILES['excel_file'])
            
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(report_content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="loan_payment_report.csv"'
            return response
    else:
        form = LoanExcelForm()
    return render(request, 'upload_loan.html', {'form': form})