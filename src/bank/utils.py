from .models import Bank, BankPayment

def create_bank_payment(bank, description, amount, payment_date):
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date)
    bank_payment.save()
    return bank_payment

def get_cash_in_hand():
    bank = Bank.objects.get(name='Cash in Hand')
    return bank
