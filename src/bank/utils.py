from .models import Bank, BankPayment

def create_bank_payment(bank, description, amount, payment_date, transaction, created_by):
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date, transaction=transaction, created_by=created_by)
    bank_payment.save()
    return bank_payment

def get_cash_in_hand():
    bank,created = Bank.objects.get_or_create(name='Cash in Hand')
    return bank

def get_bank_account():
    bank,created = Bank.objects.get_or_create(name='MoniePoint')
    return bank

def get_union_pulse():
    bank,created = Bank.objects.get_or_create(name='Union Pulse')
    return bank
