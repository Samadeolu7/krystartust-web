from decimal import Decimal

from main.models import Year
from .models import Bank, BankPayment



def create_bank_payment(bank, description, amount, payment_date, transaction, created_by):
    year = Year.current_year()
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date, transaction=transaction, created_by=created_by)
    bank_payment.save()
    return bank_payment

def get_cash_in_hand():
    year = Year.current_year()
    bank,created = Bank.objects.get_or_create(name='Cash in Hand', year=year)
    return bank

def get_cash_in_hand_dc():
    year = Year.current_year()
    bank,created = Bank.objects.get_or_create(name='Cash in Hand (DC)', year=year)
    return bank

def get_bank_account():
    year = Year.current_year()
    bank,created = Bank.objects.get_or_create(name='MoniePoint', year=year)
    return bank

def get_union_pulse():
    year = Year.current_year()
    bank,created = Bank.objects.get_or_create(name='Union Pulse', year=year)
    return bank


def get_user_and_office_banks(user):
    """
    Returns a queryset of banks that belong to the user's office or are assigned to the user.
    """
    if not user.is_authenticated:
        return Bank.objects.none()

    # Get banks for the user's office
    office_banks = Bank.objects.filter(pk=user.office.bank.pk) if user.office and user.office.bank else Bank.objects.none()

    # Get banks assigned to the user
    user_banks = user.bank.all() if hasattr(user, 'bank') else Bank.objects.none()

    # Combine the querysets
    return office_banks | user_banks