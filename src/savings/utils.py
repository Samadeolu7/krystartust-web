from bank.models import BankPayment
from .models import Savings, SavingsPayment

def register_savings(client, amount, bank):
    savings = Savings.objects.create(client=client, balance=0)
    savings.save()
    savingspayment = SavingsPayment.objects.create(client=client,savings=savings, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    savingspayment.save()
    bankpayment = BankPayment.objects.create(bank=bank, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    bankpayment.save()
    return savings