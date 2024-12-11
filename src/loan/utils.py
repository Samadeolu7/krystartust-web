from bank.models import BankPayment
from bank.utils import create_bank_payment, get_bank_account, get_cash_in_hand
from liability.models import LiabilityPayment
from liability.utils import create_union_contribution_income_payment
from .models import Loan, LoanPayment, LoanRepaymentSchedule
from income.utils import create_administrative_fee_income_payment, create_income_payment, create_loan_registration_fee_income_payment, create_risk_premium_income_payment, create_sms_fee_income_payment, get_loan_interest_income
from income.models import IncomePayment
from django.db import transaction
from main.utils import verify_trial_balance
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from administration.models import Transaction, Approval
import logging

logger = logging.getLogger(__name__)


def register_loan(client, amount, interest, loan_type, duration, risk_premium, start_date, end_date, emi, status):
    loan = Loan.objects.create(client=client, amount=amount, interest=interest, loan_type=loan_type, duration=duration, risk_premium=risk_premium, start_date=start_date, end_date=end_date, emi=emi, status=status)
    loan.save()
    income = get_loan_interest_income()
    interest = create_income_payment(client.bank, income, f'intrest on {loan.client.name} loan', loan.interest, start_date)
    

def create_loan_payment(client, loan,amount,date):
    loan_payment_schedule = LoanRepaymentSchedule.objects.filter(loan=loan,is_paid=False).first()
    loan_payment = LoanPayment.objects.create(client=client, loan=loan, amount=amount, payment_date=date, payment_schedule=loan_payment_schedule)
    loan_payment.save()
    loan_payment_schedule.is_paid = True
    loan_payment_schedule.payment_date = date
    loan_payment_schedule.save()
    bank = get_cash_in_hand()
    bank_payment = create_bank_payment(bank, f'Loan payment from {client.name}', amount, date)
    return loan_payment

def send_for_approval(form, user):
    try:
        with transaction.atomic():
            loan = form.save(commit=False)
            client = loan.client
            loan.balance = 0
            # Check for existing active loan
            existing_loan = Loan.objects.filter(client=client, status='Active').first()
            if existing_loan and not existing_loan.is_defaulted:
                # Update the balance of the new loan
                loan.balance += existing_loan.balance

                # Add comment to approval
                comment = f'Client had an existing loan with balance {existing_loan.balance}.'
            elif existing_loan and existing_loan.is_defaulted:

                raise Exception('Client has defaulted on a previous loan.')
            else:
                comment = 'New loan application.'
        
            loan.balance += loan.amount * (Decimal(1) + (Decimal(loan.interest) / Decimal(100)))
            loan_type = loan.loan_type
            if loan_type == 'Daily':
                loan.end_date = loan.start_date + timedelta(days=loan.duration)
            elif loan_type == 'Weekly':
                loan.end_date = loan.start_date + timedelta(weeks=loan.duration)
            else:
                loan.end_date = loan.start_date + timedelta(weeks=loan.duration * 4)
            loan.emi = loan.balance / loan.duration
            loan.status = 'Active'
            loan.created_by = user
            loan.save()

            tran = Transaction(description=f'Loan disbursement to {loan.client.name}')
            tran.save(prefix='LOA')
            loan.transaction = tran
            loan.save()

            approval = Approval.objects.create(
                type='loan',
                content_object=loan,
                content_type=ContentType.objects.get_for_model(Loan),
                comment=comment,
                object_id=loan.id,
                user=user,
            )

            registration_fee = form.cleaned_data.get('registration_fee')
            bank = form.cleaned_data.get('bank')
            admin_fees = form.cleaned_data.get('admin_fees')
            sms_fees = form.cleaned_data.get('sms_fees')
            start_date = loan.start_date
            amount = loan.amount

            if admin_fees:
                admin_fee_amount = Decimal(admin_fees) * Decimal(amount) / Decimal(100)
                create_administrative_fee_income_payment(bank, admin_fee_amount, start_date, f'Administrative Fee for {loan.client.name}', tran, user)

            if registration_fee:
                create_loan_registration_fee_income_payment(bank, registration_fee, start_date, f'Loan Registration Fee for {loan.client.name}', tran, user)

            if sms_fees:
                create_sms_fee_income_payment(bank, sms_fees, start_date, f'SMS Fee for {loan.client.name}', tran, user)

            risk_premium_amount = Decimal(loan.risk_premium) * Decimal(amount) / 100
            create_risk_premium_income_payment(bank, risk_premium_amount, start_date, f'Risk Premium for {loan.client.name}', tran, user)

            union = form.cleaned_data.get('union_contribution')
            create_union_contribution_income_payment(bank, start_date, union, f'Union Contribution for {loan.client.name}', tran, user)

            approval.save()
            verify_trial_balance()

            return approval
    except Exception as e:
        raise
    

def approve_loan(approval, user):
    with transaction.atomic():
        approval.approved = True
        approval.approved_by = user
        approval.approved_at = timezone.now()
        approval.save()

        loan = approval.content_object
        client = loan.client
        loan.approved = True
        loan.save()

        existing_loan = Loan.objects.filter(client=client, status='Active').exclude(id=loan.id).first()
        if existing_loan and loan.loan_type == existing_loan.loan_type:
            existing_loan.status = 'Closed'
            existing_loan.balance = 0
            existing_loan.save()
            LoanRepaymentSchedule.objects.filter(loan=existing_loan).delete()

        loan_type = loan.loan_type
        duration = loan.duration
        start_date = loan.start_date
        amount = loan.amount
        
        bank = get_bank_account()
        create_bank_payment(bank, f'Loan disbursement to {loan.client.name}', -amount, start_date,loan.transaction, user)

        time_increment = {
            'Daily': timedelta(days=1),
            'Weekly': timedelta(weeks=1),
            'Monthly': relativedelta(months=1),
            
        }.get(loan_type, timedelta(weeks=1))

        if loan_type == "Monthly":
            date = start_date + relativedelta(months=1)
        if loan_type == "Weekly":
            date = start_date + timedelta(weeks=2)
        if loan_type == "Daily":
            date = start_date + timedelta(days=1)

        amount_due = loan.balance / duration
        for i in range(duration):
            due_date = date + (i * time_increment)

            LoanRepaymentSchedule.objects.create(
                loan=loan,
                due_date=due_date,
                amount_due=amount_due,
            )

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
            transaction=loan.transaction,
            created_by=user,    
        )
        income_payment.save()

        verify_trial_balance()

def disapprove_loan(approval, user):
    with transaction.atomic():
        
        loan = approval.content_object
        loan.status = 'Rejected'
        tran = loan.transaction
        
        income_payments = IncomePayment.objects.filter(transaction=tran)
        for income_payment in income_payments:
            income_payment.delete()

        bank_payments = BankPayment.objects.filter(transaction=tran)
        for bank_payment in bank_payments:
            bank_payment.delete()

        liability_payments = LiabilityPayment.objects.filter(transaction=tran)
        for liability_payment in liability_payments:
            liability_payment.delete()

        

        loan.save()
        approval.rejected = True
        approval.approved_by = user
        approval.approved_at = timezone.now()
        approval.save()
        if loan.pk:
            loan.delete()
        tran.delete()
        verify_trial_balance()