from liability.models import Liability
from .models import IncomePayment, Income, IDFee, RegistrationFee, RiskPremium, UnionContribution
from bank.models import BankPayment, Bank
from main.models import Year

from bank.utils import get_cash_in_hand, get_union_pulse



def get_loan_interest_income(type):
    YEAR = Year.current_year()
    if type == 'Daily':
        return Income.objects.get_or_create(name='Daily Loan Interest', description='Loan Interest Income Daily', year=YEAR)[0]
    elif type == 'Weekly':
        return Income.objects.get_or_create(name='Weekly Loan Interest', description='Loan Interest Income Weekly', year=YEAR)[0]
    else:
        return Income.objects.get_or_create(name='Monthly Loan Interest', description='Loan Interest Income Monthly', year=YEAR)[0]

def get_registration_fee_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Registration Fee', description='Registration Fee Income', year=YEAR)[0]

def get_id_fee_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='ID Fee', description='ID Fee Income', year=YEAR)[0]

def get_risk_premium_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Risk Premium', description='Risk Premium Income', year=YEAR)[0]


def create_income_payment(bank,income, description, amount , payment_date):
    income_payment = IncomePayment.objects.create(income=income, description=description, amount=amount, payment_date=payment_date)
    income_payment.save()
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date)
    bank_payment.save()
    return income_payment

def create_id_fee_income_payment(payment_date):
    income = get_id_fee_income()
    amount = IDFee.objects.all().first().amount
    bank = get_cash_in_hand()
    return create_income_payment(bank=bank, income=income, description='ID Fee', amount=amount, payment_date=payment_date)

def create_registration_fee_income_payment( payment_date):
    income = get_registration_fee_income()
    amount = RegistrationFee.objects.all().first().amount
    bank = get_cash_in_hand()
    return create_income_payment(bank=bank, income=income, description='Registration Fee', amount=amount, payment_date=payment_date)

def create_loan_interest_income_payment( amount, payment_date):
    income = get_loan_interest_income()
    income_payment = IncomePayment.objects.create(income=income, description='Loan Interest', amount=amount, payment_date=payment_date)
    income_payment.save()
    return income_payment

def create_risk_premium_income_payment( amount,payment_date):
    income = get_risk_premium_income()
    bank = get_cash_in_hand()
    return create_income_payment(bank=bank, income=income, description='Risk Premium', amount=amount, payment_date=payment_date)

def get_loan_registration_fee_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Loan Registration Fee', description='Loan Registration Fee Income', year=YEAR)[0]

def create_loan_registration_fee_income_payment( amount,payment_date):
    income = get_loan_registration_fee_income()
    bank = get_cash_in_hand()
    return create_income_payment(bank=bank, income=income, description='Loan Registration Fee', amount=amount, payment_date=payment_date)

def get_administrative_fee_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Administrative Fee', description='Administrative Fee Income', year=YEAR)[0]
   
def create_administrative_fee_income_payment( amount,payment_date):
    income = get_administrative_fee_income()
    bank = get_cash_in_hand()
    return create_income_payment(bank=bank, income=income, description='Administrative Fee', amount=amount, payment_date=payment_date)

def get_income_balance(income_id):
    income = Income.objects.get(id=income_id)
    income_payments = IncomePayment.objects.filter(income=income)
    total_income_payment = 0
    for payment in income_payments:
        total_income_payment += payment.amount
    income_balance = income.balance_bf + total_income_payment
    return income_balance

def get_income_balance_by_year(year):
    incomes = Income.objects.filter(year=year)
    income_balance = 0
    for income in incomes:
        income_balance += get_income_balance(income.id)
    return income_balance

def get_income_balance_by_month(year, month):
    incomes = Income.objects.filter(year=year)
    income_balance = 0
    for income in incomes:
        income_payments = IncomePayment.objects.filter(income=income, payment_date__month=month)
        total_income_payment = 0
        for payment in income_payments:
            total_income_payment += payment.amount
        income_balance += income.balance_bf + total_income_payment
    return income_balance

def get_total_income_balance():
    incomes = Income.objects.all()
    income_balance = 0
    for income in incomes:
        income_balance += get_income_balance(income.id)
    return income_balance

def get_total_income_balance_by_year(year):
    incomes = Income.objects.filter(year=year)
    income_balance = 0
    for income in incomes:
        income_balance += get_income_balance(income.id)
    return income_balance

def get_total_income_balance_by_month(year, month):
    incomes = Income.objects.filter(year=year)
    income_balance = 0
    for income in incomes:
        income_payments = IncomePayment.objects.filter(income=income, payment_date__month=month)
        total_income_payment = 0
        for payment in income_payments:
            total_income_payment += payment.amount
        income_balance += income.balance_bf + total_income_payment
    return income_balance
