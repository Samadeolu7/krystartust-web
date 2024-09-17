from .models import IncomePayment, Income
from bank.models import BankPayment, Bank
from main.models import Year



def get_loan_interest_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Loan Interest', description='Loan Interest Income', year=YEAR)[0]

def get_registration_fee_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Registration Fee', description='Registration Fee Income', year=YEAR)[0]

def get_id_fee_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='ID Fee', description='ID Fee Income', year=YEAR)[0]

def get_risk_premium_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Risk Premium', description='Risk Premium Income', year=YEAR)[0]

def get_union_contribution_income():
    YEAR = Year.current_year()
    return Income.objects.get_or_create(name='Union Contribution', description='Union Contribution Income', year=YEAR)[0]

def create_income_payment(bank,income, description, amount , payment_date):
    income_payment = IncomePayment.objects.create(income=income, description=description, amount=amount, payment_date=payment_date)
    income_payment.save()
    bank_payment = BankPayment.objects.create(bank=bank, description=description, amount=amount, payment_date=payment_date)
    bank_payment.save()
    return income_payment
    

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
