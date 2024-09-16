from bank.models import BankPayment
from .models import Savings, SavingsPayment

def register_savings(client, amount, bank,created_by):
    savings = Savings.objects.create(client=client, balance=0)
    savings.save()
    savingspayment = SavingsPayment.objects.create(client=client,savings=savings, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at)
    savingspayment.save()
    bankpayment = BankPayment.objects.create(bank=bank, amount=amount, description=f'Savings for {client.name}', payment_date=savings.created_at, created_by=created_by)
    bankpayment.save()
    return savings