from bank.models import BankPayment
from bank.utils import get_cash_in_hand
from income.models import UnionContribution
from main.models import Year
from .models import Liability, LiabilityPayment


def create_liability_payment(bank,liability, amount, description, payment_date, transaction, created_by):
    liability_payment = LiabilityPayment.objects.create(liability=liability, amount=amount, description=description, payment_date=payment_date, transaction=transaction, created_by=created_by)
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date, transaction=transaction, created_by=created_by)

    return liability_payment


def get_union_contribution_income():
    YEAR = Year.current_year()
    return Liability.objects.get_or_create(name='Union Contribution', description='Union Contribution Income', year=YEAR)[0]

def create_union_contribution_income_payment( bank,payment_date,amount,description,tran,created_by):
    liability = get_union_contribution_income()
    return create_liability_payment(bank=bank, liability=liability, description=description, amount=amount, payment_date=payment_date, transaction=tran, created_by=created_by)