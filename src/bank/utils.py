from .models import Bank, BankPayment

def create_bank_payment(bank, description, amount, created_by, payment_date):
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, created_by=created_by, payment_date=payment_date)
    bank_payment.save()
    return bank_payment
