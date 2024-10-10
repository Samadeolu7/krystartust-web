from bank.models import BankPayment
from bank.utils import get_cash_in_hand
from income.models import UnionContribution
from main.models import Year
from .models import Liability


def create_liability_payment(bank,liability, amount, description, payment_date):
    liability.record_payment(amount, description, payment_date)
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date)
    bank_payment.save()
    return liability


def get_union_contribution_income():
    YEAR = Year.current_year()
    return Liability.objects.get_or_create(name='Union Contribution', description='Union Contribution Income', year=YEAR)[0]

def create_union_contribution_income_payment( payment_date,amount,description):
    liability = get_union_contribution_income()
    bank = get_cash_in_hand()
    return create_liability_payment(bank=bank, liability=liability, description=description, amount=amount, payment_date=payment_date)