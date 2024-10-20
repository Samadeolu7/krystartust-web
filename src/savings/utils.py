import logging
from bank.models import BankPayment
from bank.utils import get_cash_in_hand, create_bank_payment
from .models import Savings, SavingsPayment, CompulsorySavings

def register_savings(bank,client, amount, date, transaction, user): 
    savings = Savings.objects.create(client=client, balance=0)
    savings.save()
    savingspayment = SavingsPayment.objects.create(client=client,savings=savings, amount=amount, description=f'Savings for {client.name}', payment_date=date, created_by=user, transaction=transaction)
    savingspayment.save()
    bank = get_cash_in_hand()
    bankpayment = BankPayment.objects.create(bank=bank, amount=amount, description=f'Savings for {client.name}', payment_date=date, created_by=user, transaction=transaction)
    bankpayment.save()
    return savings

def create_compulsory_savings(client,amount,transaction, user):

    register_savings(client=client, amount=amount, date=transaction.payment_date, transaction=transaction, user=user)



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
        raise e