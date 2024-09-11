from django.shortcuts import redirect, render
from django.contrib import messages

from client.models import Client
from savings.models import Savings, SavingsPayment
from main.models import ClientGroup as Group
from .models import Loan, LoanPayment, LoanRepaymentSchedule
from .forms import LoanForm, LoanRegistrationForm, LoanPaymentForm

from datetime import timedelta

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
                loan.balance -= loan_payment.amount
                loan.save()
            else:
                messages.error(request, "Loan not found for the client.")
                return render(request, 'payments/loan_payment_form.html', {'form': form})
            
            # Save the payment after modifying the balance and schedule
            loan_payment.save()

            messages.success(request, "Loan payment processed successfully.")
            return redirect('success_page')  # Replace with your success page URL name
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")
    else:
        form = LoanPaymentForm()  # Corrected the form initialization
    
    return render(request, 'loan_payment_form.html', {'form': form})


def loan_registration(request):
    if request.method == 'POST':
        form = LoanRegistrationForm(request.POST)
        if form.is_valid():
            # Save the loan form data to create a new Loan instance
            loan = form.save(commit=False)
            loan.save()  # Save the loan instance first to access it for schedule creation
            
            # Get the loan details
            loan_type = loan.loan_type
            duration = loan.duration
            start_date = loan.start_date
            amount = loan.amount
            interest = loan.interest
            risk_premium = loan.risk_premium
            
            # Calculate the total amount due per schedule
            amount_due = amount + (amount * interest) + risk_premium
            
            # Determine the increment based on loan type
            time_increment = {
                'Daily': timedelta(days=1),
                'Weekly': timedelta(weeks=1),
                # Add more loan types as needed
            }.get(loan_type, timedelta(weeks=1))  # Default to weekly if the loan type is not specifically listed
            
            # Create repayment schedule based on the loan type and duration
            for i in range(duration):
                due_date = start_date + (i * time_increment)
                LoanRepaymentSchedule.objects.create(
                    loan=loan,
                    due_date=due_date,
                    amount_due=amount_due
                )
            
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
    loan_payments = LoanPayment.objects.filter(loan__in=defaulters)
    
    context = {
        'defaulters': defaulters,
        'clients': clients,
        'loan_payments': loan_payments,
        'schedule': schedule,
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
