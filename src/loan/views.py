
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction

from datetime import date, timedelta
from decimal import Decimal

from administration.decorators import allowed_users
from administration.models import Transaction
from administration.utils import validate_month_status
from client.models import Client
from income.models import IncomePayment
from loan.excel_utils import bulk_create_loans_from_excel, loan_from_excel
from loan.utils import send_for_approval
from savings.models import Savings, SavingsPayment
from main.models import ClientGroup as Group
from .models import Loan, LoanPayment, LoanRepaymentSchedule
from .forms import GuarantorForm, LoanRegistrationForm, LoanPaymentForm, LoanExcelForm, LoanUploadForm
from bank.utils import create_bank_payment
from main.utils import verify_trial_balance


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
                try:
                    validate_month_status(loan_payment.payment_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'loan_payment_form.html', {'form': form})
                loan_id = loan_payment.loan.id
                
                # Retrieve and update the repayment schedule
                schedule = form.payment_schedule
                if schedule.is_paid:
                    messages.error(request, "Payment schedule has already been marked as paid.")
                    raise ValueError("Payment schedule has already been marked as paid.")
                else:
                    schedule.is_paid = True
                    schedule.payment_date = loan_payment.payment_date
                    schedule.save()
                
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
                tran = Transaction.objects.create(f'Loan payment from {loan.client.name}')
                tran.save(prefix='LP')
                loan_payment.transaction = tran
                loan_payment.created_by = request.user
                loan_payment.save()

                # Update the bank balance
                bank = form.cleaned_data.get('bank')
                create_bank_payment(bank, f'Loan payment from {loan.client.name}',loan_payment.amount, loan_payment.payment_date, loan_payment, request.user)

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
        loans = Loan.objects.filter(client_id=client_id).order_by('-created_at')
        payment_schedules = LoanRepaymentSchedule.objects.filter(loan__in=loans, is_paid=False).order_by('due_date')
        return JsonResponse(list(payment_schedules.values('id', 'due_date', 'amount_due')), safe=False)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'Loan not found'}, status=404)

@login_required
@allowed_users(allowed_roles=['Admin'])
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
@allowed_users(allowed_roles=['Admin', 'Manager'])
def loan_registration(request):
    if request.method == 'POST':
        form = LoanRegistrationForm(request.POST)
        if form.is_valid():
            user = request.user
            loan_date = form.cleaned_data.get('start_date')

            try:
                validate_month_status(loan_date)
            except Exception as e:
                form.add_error(None, e)
                return render(request, 'loan_register.html', {'form': form})
            loan = send_for_approval(form, user)
            messages.success(request, "Loan registered successfully and repayment schedule created.")
            return redirect('guarantor_for_loan', loan_id=loan.id) 
        else:
            messages.error(request, "There was an error with the form. Please correct it below.")
    else:
        form = LoanRegistrationForm()

    return render(request, 'loan_register.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def guarantor_for_loan(request, loan_id):
    form = GuarantorForm()
    loan = Loan.objects.get(id=loan_id)
    form.fields['loan'].initial = loan
    if request.method == 'POST':
        form = GuarantorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Guarantor added successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error with the form. Please correct it below.")

    return render(request, 'guarantor_form.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def loan_detail(request, id):
    loan = Loan.objects.filter(id=id).first()
    loan_payments = LoanPayment.objects.filter(loan=loan)
    loan_repayment_schedules = LoanRepaymentSchedule.objects.filter(loan=loan)
    loan_interest_amount = Decimal(loan.interest) * Decimal(loan.amount) / Decimal(100)
    print(loan.guarantor)
    context = {
        'loan': loan,
        'loan_payments': loan_payments,
        'loan_schedules': loan_repayment_schedules,
        'loan_interest_amount': loan_interest_amount,
    }
    return render(request, 'loan_detail.html', context)

@login_required
def loan_schedule(request, loan_id):
    schedules = LoanRepaymentSchedule.objects.filter(loan_id=loan_id).order_by('due_date')
    return render(request, 'loan_schedule.html', {'schedules': schedules})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
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
@allowed_users(allowed_roles=['Admin', 'Manager'])
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
@allowed_users(allowed_roles=['Admin'])
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


@login_required
@csrf_exempt
def extend_loan(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        try:
            loan = Loan.objects.get(id=loan_id)
            # Perform the extension logic here
            unpaid_schedules = LoanRepaymentSchedule.objects.filter(loan=loan, is_paid=False)
            #extend due date of all unpaid schedules by 7 days
            for schedule in unpaid_schedules:
                schedule.due_date += timedelta(days=7)
                schedule.save()
            return JsonResponse({'success': True})
        except Loan.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Loan not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})