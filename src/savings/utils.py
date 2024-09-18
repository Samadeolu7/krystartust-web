from bank.models import BankPayment
from bank.utils import get_cash_in_hand
from .models import Savings, SavingsPayment, CompulsorySavings

def register_savings(client, amount, bank):
    savings = Savings.objects.create(client=client, balance=0)
    savings.save()
    savingspayment = SavingsPayment.objects.create(client=client,savings=savings, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    savingspayment.save()
    bankpayment = BankPayment.objects.create(bank=bank, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    bankpayment.save()
    return savings

def create_compulsory_savings(client):
    compulsory_savings = CompulsorySavings.objects.all().first()
    if compulsory_savings:
        register_savings(client=client, amount=compulsory_savings.amount, bank=get_cash_in_hand())
    return compulsory_savings