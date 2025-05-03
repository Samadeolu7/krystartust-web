from datetime import datetime, timedelta
from client.models import Client

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType


from administration.models import Approval, Transaction
from administration.utils import validate_month_status
from loan.models import LoanPayment
from main.models import ClientGroup, Year
from main.utils import verify_trial_balance
from savings.models import SavingsPayment
from .forms import BankForm, CashTransferForm, DateRangeForm, ReversePaymentForm
from .models import Bank, BankPayment, PendingCashTransfer
from administration.decorators import allowed_users
from .excel_utils import bank_to_excel
# Create your views here.

@login_required
@allowed_users(allowed_roles=['Admin'])
def create_bank(request):
    form = BankForm()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'create_bank.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin'])
def create_bank_asset(request):
    form = BankForm()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            form.instance.type = Bank.ASSET
            form.save()
    return render(request, 'create_bank.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_list(request):
    current_year = Year.current_year()
    banks = Bank.objects.filter(year=current_year, type=Bank.BANK).all()
    has_previous_years_banks = Bank.objects.filter(year__lt=current_year, type=Bank.BANK).exists()
    context = {
        'banks': banks,
        'current_year': current_year,
        'has_previous_years_banks': has_previous_years_banks
    }
    return render(request, 'bank_list.html', context)

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_list_asset(request):
    current_year = Year.current_year()
    banks = Bank.objects.filter(year=current_year, type=Bank.ASSET).all()
    has_previous_years_banks = Bank.objects.filter(year__lt=current_year, type=Bank.ASSET).exists()
    context = {
        'banks': banks,
        'current_year': current_year,
        'has_previous_years_banks': has_previous_years_banks
    }
    return render(request, 'bank_list.html', context)

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def previous_years_banks(request):
    current_year = Year.current_year()
    previous_years_banks = Bank.objects.filter(year__lt=current_year).all()
    return render(request, 'bank_list.html', {'banks': previous_years_banks})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_detail(request, pk):
    bank = Bank.objects.get(pk=pk)
    today = timezone.now().date()
    start_date = today - timedelta(days=30)

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Ensure the date range does not exceed 2 months
        else:
            end_date = today
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': today})
        end_date = today

    bank_payment = bank.payments.filter(payment_date__range=[start_date, end_date]).select_related('transaction')

    context = {
        'bank': bank,
        'bank_payment': bank_payment,
        'form': form,
    }
    return render(request, 'bank_detail.html', context)

# views.py

@login_required
def cash_transfer(request):
    if request.method == 'POST':
        form = CashTransferForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payment_date = form.cleaned_data['payment_date']
                try:
                    validate_month_status(payment_date)
                except Exception as e:
                    form.add_error(None, e)
                    return render(request, 'cash_transfer.html', {'form': form})
                source_bank = form.cleaned_data['source_bank']
                destination_bank = form.cleaned_data['destination_bank']
                amount = form.cleaned_data['amount']
                description = form.cleaned_data['description']

                # Create a pending cash transfer
                pending_transfer = PendingCashTransfer.objects.create(
                    source_bank=source_bank,
                    destination_bank=destination_bank,
                    amount=amount,
                    description=description,
                    payment_date=payment_date,
                    created_by=request.user
                )

                # Create an approval request
                Approval.objects.create(
                    type=Approval.Cash_Transfer,
                    user=request.user,
                    content_object=pending_transfer,
                    content_type=ContentType.objects.get_for_model(PendingCashTransfer),
                    object_id=pending_transfer.id,
                    comment=f"Cash transfer from {source_bank.name} to {destination_bank.name} - {amount}"
                )

            return redirect('dashboard')
    else:
        form = CashTransferForm()

    return render(request, 'cash_transfer.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def bank_to_excel_view(request, pk):

    bank = Bank.objects.get(pk=pk)
    df = bank_to_excel(bank)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename={bank.name}_payments.xlsx'
    df.to_excel(response, index=False)
    return response

@login_required
@allowed_users(allowed_roles=['Admin'])
def payment_reversal(request):
    form = ReversePaymentForm()
    if request.method == 'POST':
        form = ReversePaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                type = form.cleaned_data['type']
                bank = form.cleaned_data['bank']
                payment = form.cleaned_data['payment']
                reversal_date = form.cleaned_data['reversal_date']
                reason = form.cleaned_data['reason']

                # Create a new transaction for the reversal
                tran = Transaction(description=f'Payment reversal: {payment.description} - {reason}')
                tran.save(prefix='REV')

                # Create a new BankPayment for the reversal
                BankPayment.objects.create(
                    bank=bank,
                    description=f'Payment reversal: {payment.description} - {reason}',
                    amount=-payment.amount,
                    bank_balance=bank.balance - payment.amount,
                    payment_date=reversal_date,
                    transaction=tran
                )
                if type == 'COM':
                    # Create a new BankPayment for the reversal
                    
                    loan_payment = LoanPayment.objects.get(transaction=payment.transaction)

                    schedule = loan_payment.payment_schedule
                    if schedule:
                        schedule.is_paid = False
                        schedule.payment_date = None
                        loan_payment.payment_schedule = None
                        schedule.save()
                    loan_payment.save()
                    LoanPayment.objects.create(
                        client=loan_payment.client,
                        loan=loan_payment.loan,
                        amount=-loan_payment.amount,
                        balance=loan_payment.loan.balance - loan_payment.amount,
                        payment_date=reversal_date,
                        transaction=tran
                    )
                    savings_payment = SavingsPayment.objects.get(transaction=payment.transaction)
                    SavingsPayment.objects.create(
                        client=savings_payment.client,
                        savings=savings_payment.savings,
                        description=f'Payment reversal: {payment.description} - {reason}',
                        amount=-savings_payment.amount,
                        balance=savings_payment.savings.balance - savings_payment.amount,
                        payment_date=reversal_date,
                        transaction=tran
                    )

                elif type == 'SVS':
                    savings_payment = SavingsPayment.objects.get(transaction=payment.transaction)
                    SavingsPayment.objects.create(
                        client=savings_payment.client,
                        savings=savings_payment.savings,
                        description=f'Payment reversal: {payment.description} - {reason}',
                        amount=-savings_payment.amount,
                        balance=savings_payment.savings.balance - savings_payment.amount,
                        payment_date=reversal_date,
                        transaction=tran
                    )
                elif type == 'LOA':
                    loan_payment = LoanPayment.objects.get(transaction=payment.transaction)
                    repayment_schedule = loan_payment.payment_schedule
                    if repayment_schedule:
                        repayment_schedule.is_paid = False
                        repayment_schedule.payment_date = None
                        repayment_schedule.save()
                        loan_payment.payment_schedule = None
                    loan_payment.save()
                    
                    LoanPayment.objects.create(
                        client=loan_payment.client,
                        loan=loan_payment.loan,
                        description=f'Payment reversal: {payment.description} - {reason}',
                        amount=-loan_payment.amount,
                        loan_balance=loan_payment.loan.balance - loan_payment.amount,
                        payment_date=reversal_date,
                        transaction=tran
                    )
                elif type == 'GCOM':
                    # Extract the client name from the payment description
                    if "Group Combined Payment for " in payment.description:
                        client_name = payment.description.split("Group Combined Payment for ")[1].strip()
                    else:
                        client_name = None  # Handle cases where the format is unexpected
                
                    if client_name:
                        # Fetch the client object using the extracted name
                        try:
                            client = Client.objects.get(name=client_name)
                            if not client:
                                form.add_error(None, f"Client '{client_name}' not found.")
                                raise ValueError(f"Client '{client_name}' not found.")
                            try:
                                loan_payment = LoanPayment.objects.get(transaction=payment.transaction,client=client)
                            except LoanPayment.DoesNotExist:
                                loan_payment = None
                            savings_payment = None
                            if loan_payment == None or loan_payment.amount != payment.amount:
                                savings_payment = SavingsPayment.objects.get(transaction=payment.transaction,client=client)
                            
                            schedule = loan_payment.payment_schedule
                            if schedule:
                                schedule.is_paid = False
                                schedule.payment_date = None
                                loan_payment.payment_schedule = None
                                schedule.save()

                            # Create a new LoanPayment for the reversal
                            LoanPayment.objects.create(
                                client=loan_payment.client,
                                loan=loan_payment.loan,
                                amount=-loan_payment.amount,
                                balance=loan_payment.loan.balance - loan_payment.amount,
                                payment_date=reversal_date,
                                transaction=tran
                            )
                            # Create a new SavingsPayment for the reversal
                            if savings_payment:
                                SavingsPayment.objects.create(
                                    client=savings_payment.client,
                                    savings=savings_payment.savings,
                                    description=f'Payment reversal: {payment.description} - {reason}',
                                    amount=-savings_payment.amount,
                                    balance=savings_payment.savings.balance - savings_payment.amount,
                                    payment_date=reversal_date,
                                    transaction=tran
                                )
                            # Perform the reversal logic for the specific client
                            # Example: Reverse loan or savings payment for the client
                        except LoanPayment.DoesNotExist:
                            form.add_error(None, f"Loan payment for client '{client_name}' not found.")
                            raise ValueError(f"Loan payment for client '{client_name}' not found.")
                        except :
                            form.add_error(None, f"Savings payment for client '{client_name}' not found.")
                            raise ValueError(f"Savings payment for client '{client_name}' not found.")
                    else:
                        form.add_error(None, "Unable to extract client name from the payment description.")

                verify_trial_balance()

            return redirect('dashboard')
    else:
        form = ReversePaymentForm()

    return render(request, 'payment_reversal.html', {'form': form})

@login_required
def fetch_gcom_clients(request):
    payment_id = request.GET.get('payment_id')
    if not payment_id:
        return JsonResponse({'error': 'Payment ID is required.'}, status=400)

    try:
        payment = BankPayment.objects.get(id=payment_id)
        tran = payment.transaction
        client_data = []
        for payment in tran.loan_payment.all():
            if payment.loan:
                client_data.append(payment.loan.client)
        return JsonResponse({'clients': client_data})
    except BankPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found.'}, status=404)
    except ClientGroup.DoesNotExist:
        return JsonResponse({'error': 'Group not found.'}, status=404)


def update_payments(request):
    type = request.GET.get('type')
    bank_id = int(request.GET.get('bank'))
    payment_date = request.GET.get('payment_date')
    payments = BankPayment.objects.filter(
        bank=bank_id,
        payment_date=payment_date,
        transaction__reference_number__startswith=type[:3]
    )

    html = render_to_string('payments_dropdown_list_options.html', {'payments': payments})
    return JsonResponse(html, safe=False)