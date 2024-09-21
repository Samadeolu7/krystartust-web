from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from client.models import Client
from income.models import IncomePayment
from loan.excel_utils import bulk_create_loans_from_excel, loan_from_excel
from savings.models import Savings, SavingsPayment
from bank.models import BankPayment
from main.models import ClientGroup as Group
from .models import Loan, LoanPayment, LoanRepaymentSchedule
from .forms import LoanRegistrationForm, LoanPaymentForm, LoanExcelForm, LoanUploadForm

from bank.utils import create_bank_payment

from income.utils import get_loan_interest_income, get_risk_premium_income, get_union_contribution_income

from datetime import date, timedelta

# Create your views here.

def transaction_history(request, client_id):
    transactions = Loan.objects.filter(client_id=client_id).order_by('-created_at')
    return render(request, 'transaction_history.html', {'transactions': transactions})


def loan_payment(request):
    if request.method == 'POST':
        form = LoanPaymentForm(request.POST)
        if form.is_valid():
            # Save the loan payment record
            loan_payment = form.save(commit=False)
            client_id = loan_payment.client.id
            
            # Retrieve and update the repayment schedule
            schedule = LoanRepaymentSchedule.objects.filter(id=loan_payment.payment_schedule.id).first()
            if schedule:
                schedule.is_paid = True
                schedule.save()
            else:
                messages.error(request, "Payment schedule not found.")
                return render(request, 'loan_payment_form.html', {'form': form})
            
            # Update the loan balance
            loan = Loan.objects.filter(client_id=client_id).first()
            if loan:
                loan.balance -= Decimal(loan_payment.amount)
                loan.save()
            else:
                messages.error(request, "Loan not found for the client.")
                return render(request, 'payments/loan_payment_form.html', {'form': form})
            
            # Save the payment after modifying the balance and schedule
            loan_payment.save()

            # Update the bank balance
            bank = form.cleaned_data.get('bank')
            create_bank_payment(bank, loan_payment.amount, f'Loan payment from {loan.client.name}', loan_payment.payment_date)
            

            messages.success(request, "Loan payment processed successfully.")
            return redirect('success_page')  # Replace with your success page URL name
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")
    else:
        form = LoanPaymentForm()  # Corrected the form initialization
    
    return render(request, 'loan_payment_form.html', {'form': form})

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

def loan_registration(request):
    if request.method == 'POST':
        form = LoanRegistrationForm(request.POST)
        if form.is_valid():
            # Save the loan form data to create a new Loan instance
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
            bank = form.cleaned_data.get('bank')

            # Calculate the total amount due per schedule

            # Determine the increment based on loan type
            time_increment = {
                'Daily': timedelta(days=1),
                'Weekly': timedelta(weeks=1),
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
            interest_income = get_loan_interest_income()
            income_payment = IncomePayment.objects.create(
                income=interest_income,
                description=f'Interest income from {loan.client.name}',
                amount=interest_amount,
                payment_date=start_date,
            )
            income_payment.save()

            risk_premium_income = get_risk_premium_income()
            risk_premimum_amount = Decimal(loan.risk_premium) * Decimal(amount) / Decimal(100)
            risk_premium_payment = IncomePayment.objects.create(
                income=risk_premium_income,
                description=f'Risk premium from {loan.client.name}',
                amount=risk_premimum_amount,
                payment_date=start_date,
            )
            risk_premium_payment.save()

            union_contribution_income = get_union_contribution_income()
            union_contribution_amount = Decimal(form.cleaned_data.get('union_contribution'))
            union_contribution_payment = IncomePayment.objects.create(
                income=union_contribution_income,
                description=f'Union contribution from {loan.client.name}',
                amount=union_contribution_amount,
                payment_date=start_date,
            )
            union_contribution_payment.save()

            messages.success(request, "Loan registered successfully and repayment schedule created.")
            return redirect('success_page')  # Replace with your actual success page URL name
        else:
            messages.error(request, "There was an error with the form. Please correct it below.")
    else:
        form = LoanRegistrationForm()

    return render(request, 'loan_register.html', {'form': form})

def loan_detail(request, loan_id):
    loan = Loan.objects.filter(id=loan_id).first()
    return render(request, 'loan_detail.html', {'loan': loan})

def loan_schedule(request, loan_id):
    schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_id).order_by('due_date')
    return render(request, 'loan_schedule.html', {'schedules': schedules})

def loan_defaulters_report(request):
    loans = Loan.objects.filter(status='Active')
    defaulters = [loan for loan in loans if loan.is_defaulted()]
    clients = Client.objects.filter(loan__in=defaulters)
    schedule = LoanRepaymentSchedule.objects.filter(loan__in=defaulters)
    #filter fo those schedules that have the due date less than today and is_paid is False
    filtered_schedule = [schedule for schedule in schedule if schedule.due_date < date.today() and not schedule.is_paid]
    loan_payments = LoanPayment.objects.filter(loan__in=defaulters)
    
    context = {
        'defaulters': defaulters,
        'clients': clients,
        'loan_payments': loan_payments,
        'schedule': filtered_schedule,
    }

    return render(request, 'loan_defaulters_report.html', context)

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

def loan_upload(request):
    if request.method == 'POST':
        form = LoanExcelForm(request.POST, request.FILES)
        if form.is_valid():
            loan_from_excel(request.FILES['excel_file'])
            return redirect('dashboard')
    else:
        form = LoanExcelForm()
    return render(request, 'upload_loan.html', {'form': form})