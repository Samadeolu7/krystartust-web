import logging
from bank.models import BankPayment
from bank.utils import get_cash_in_hand, create_bank_payment
from .models import Savings, SavingsPayment, CompulsorySavings

def register_savings(client, amount):
    savings = Savings.objects.create(client=client, balance=0)
    savings.save()
    savingspayment = SavingsPayment.objects.create(client=client,savings=savings, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    savingspayment.save()
    bank = get_cash_in_hand()
    bankpayment = BankPayment.objects.create(bank=bank, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    bankpayment.save()
    return savings

def create_compulsory_savings(client):
    compulsory_savings = CompulsorySavings.objects.all().first()
    if compulsory_savings:
        register_savings(client=client, amount=compulsory_savings.amount)
    return compulsory_savings


def create_savings_payment(client, amount, payment_date):
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
        create_bank_payment(bank,f'Savings for {client.name}',amount, payment_date )
        return savings_payment
    except Exception as e:
        logging.error(f"Error creating savings payment for client {client.name}: {e}")
        raise