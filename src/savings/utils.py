from datetime import date, timedelta
from decimal import Decimal
import logging

from administration.models import Approval, Transaction
from bank.models import BankPayment
from bank.utils import get_cash_in_hand, create_bank_payment, get_cash_in_hand_dc
from income.utils import create_income_payment, get_dc_income
from .models import DailyContribution, Savings, SavingsPayment

from django.contrib.contenttypes.models import ContentType

def register_savings(bank,client, amount, date, transaction, user): 
    savings = Savings.objects.create(client=client, balance=0)
    savings.save()
    savingspayment = SavingsPayment.objects.create(client=client,savings=savings, amount=amount, description=f'Savings for {client.name}', payment_date=date, created_by=user, transaction=transaction)
    savingspayment.save()
    bankpayment = BankPayment.objects.create(bank=bank, amount=amount, description=f'Savings for {client.name}', payment_date=date, created_by=user, transaction=transaction)
    bankpayment.save()
    return savings

def create_compulsory_savings(client,amount,transaction, user):

    register_savings(client=client, amount=amount, date=transaction.payment_date, transaction=transaction, user=user)


def create_savings_payment(client, amount, payment_date, transaction, user):
    savings = Savings.objects.filter(client=client).first()
    if not savings:
        raise ValueError(f"No savings account found for client {client.name}")

    try:
        savings_payment = SavingsPayment.objects.create(
            client=client,
            savings=savings,
            amount=amount,
            payment_date=payment_date
        )
        bank = get_cash_in_hand()
        create_bank_payment(bank,f'Savings for {client.name}',amount, payment_date ,transaction, user)
        return savings_payment
    except Exception as e:
        logging.error(f"Error creating savings payment for client {client.name}: {e}")
        raise e
    
def create_dc_payment(daily_contribution, user):
    """
    Create a SavingsPayment record based on a DailyContribution entry.
    """
    if daily_contribution.payment_made:
        dc_month = DailyContribution.objects.filter(client_contribution=daily_contribution.client_contribution, date__month=daily_contribution.date.month, date__year=daily_contribution.date.year, payment_made=True).count()
        print(dc_month)
        if dc_month == 1:
            transaction = Transaction(description=f'Daily Contribution for {daily_contribution.date} from {daily_contribution.client_contribution.client.name}')
            transaction.save(prefix='DC')
            income = get_dc_income()
            bank = get_cash_in_hand_dc()
            amount = daily_contribution.client_contribution.amount
            create_income_payment(bank=bank, income=income, description=f'DC income for {daily_contribution.client_contribution.client.name}', amount=amount, payment_date=daily_contribution.date,transaction=transaction,user=user)
            return
 
        savings_record = Savings.objects.get(
            client=daily_contribution.client_contribution.client, 
            type=Savings.DC
        )
        #remove income if first payment of the month
        transaction = Transaction(description=f'Daily contribution for {daily_contribution.date} from {daily_contribution.client_contribution.client.name}')
        transaction.save(prefix='DC')
        savings_payment = SavingsPayment.objects.create(
            client=daily_contribution.client_contribution.client,
            savings=savings_record,
            balance=savings_record.balance + Decimal(daily_contribution.client_contribution.amount),
            description=f"Daily contribution for {daily_contribution.date}",
            amount=daily_contribution.client_contribution.amount,
            payment_date=daily_contribution.date,
            transaction_type=SavingsPayment.DC,
            approved=True,
            transaction=transaction,
            created_by=user
        )
        daily_contribution.payment = savings_payment
        daily_contribution.save()
        bank = get_cash_in_hand_dc()
        create_bank_payment(
            bank=bank,
            description=f"Daily contribution for {daily_contribution.date}, {daily_contribution.client_contribution.client.name}",
            amount=daily_contribution.client_contribution.amount,
            payment_date=daily_contribution.date,
            transaction=transaction,
            created_by=user
        )

def setup_monthly_contributions(client_contribution, month, year,user):
    """
    Create daily contributions for every weekday in a given month for a client.
    """
    first_day = date(year, month, 1)
    last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    current_date = first_day
    DailyContribution.objects.get_or_create(
                client_contribution=client_contribution,
                date=current_date,
                payment_made=True
            )
    income = get_dc_income()
    bank = get_cash_in_hand_dc()
    amount = client_contribution.amount
    transaction = Transaction(description=f'Daily Contribution for {client_contribution.client.name}')
    transaction.save(prefix='DC')
    create_income_payment(bank=bank, income=income, description=f'DC income for {client_contribution.client.name}', amount=amount, payment_date=current_date,transaction=transaction,user=user)
    current_date += timedelta(days=1)
    contributions = []
    while current_date <= last_day:
    
        contributions.append(DailyContribution(
            client_contribution=client_contribution,
            date=current_date,
            payment_made=False
        ))
        current_date += timedelta(days=1)
    DailyContribution.objects.bulk_create(contributions)

def make_withdrawal(form, user):
    withdrawal = form.save(commit=False)
    tran = Transaction(description=f'Withdrawal for {withdrawal.savings.client.name}')
    tran.save(prefix='WDL')
    withdrawal.transaction = tran

    withdrawal.save()

    approval = Approval.objects.create(
        type=Approval.Withdrawal,
        content_object=withdrawal,
        content_type=ContentType.objects.get_for_model(SavingsPayment),
        user=user,
        object_id=withdrawal.id
    )
                