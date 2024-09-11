from .models import Loan, LoanPayment
from income.utils import create_income_payment, get_loan_interest_income
from income.models import Income

def register_loan(client, amount, interest, loan_type, duration, risk_premium, start_date, end_date, emi, status):
    loan = Loan.objects.create(client=client, amount=amount, interest=interest, loan_type=loan_type, duration=duration, risk_premium=risk_premium, start_date=start_date, end_date=end_date, emi=emi, status=status)
    loan.save()
    income = get_loan_interest_income()
    interest = create_income_payment(client.bank, income, f'intrest on {loan.client.name} loan', loan.interest, client.created_by, start_date)
    

def create_loan_payment(client, loan, emi, amount, payment_schedule, payment_date):
    loan_payment = LoanPayment.objects.create(client=client, loan=loan, emi=emi, amount=amount, payment_schedule=payment_schedule, payment_date=payment_date)
    loan_payment.save()
    return loan_payment