from bank.models import Bank, BankPayment
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from loan.models import Loan, LoanPayment
from main.models import Year, YearEndEntry
from savings.models import Savings, SavingsPayment

from django.db import transaction
from django.utils import timezone

from django.db.models import Sum


def verify_trial_balance():
    year = Year.current_year()
    # Aggregate sums in a single query for each model
    total_incomes = Income.objects.filter(year=year).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_expenses = Expense.objects.filter(year=year).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_savings = Savings.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_loans = Loan.objects.filter(approved=True).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_banks = Bank.objects.filter(year=year).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_liability = Liability.objects.filter(year=year).aggregate(total=Sum('balance')).get('total', 0) or 0
    # Calculate total credit and debit
    total_credit = total_incomes + total_savings + total_liability
    total_debit = total_expenses + total_loans + total_banks 

    if abs(total_credit - total_debit) <= 1:
        if total_credit == total_debit:
            return True
        else:
            control_difference = abs(total_credit - total_debit)
            control_account = Bank.objects.filter(name='Control Account').first()
            if control_account:
                bank_payment = BankPayment(
                    bank=control_account,
                    amount=control_difference,
                    payment_date=timezone.now(),
                    description='Control Account Adjustment for Trial Balance',
                )
                bank_payment.save()
                return True
    else:
        raise ValueError(
            f'Trial balance does not match. Credit: {total_credit}, '
            f'Debit: {total_debit}, '
            f'Difference: {total_credit - total_debit}'
        )

def close_trial_balance(year):
    pass


def close_balance_sheet(year):
    pass

def close_profit_and_loss(year):

    incomes_by_month = IncomePayment.objects.filter(created_at__year=year-1).values(
        'payment_date__month', 'income__name'
    ).annotate(monthly_total=Sum('amount'))

    expenses_by_month = ExpensePayment.objects.filter(payment_date__year=year-1).values(
        'payment_date__month', 'expense__name', 'expense__expense_type__name'
    ).annotate(monthly_total=Sum('amount'))

    yearly_income_total = 0
    yearly_expense_total = 0

    # Process incomes
    for income in incomes_by_month:
        total = income['monthly_total']
        yearly_income_total += total

    # Process expenses
    for expense in expenses_by_month:
        total = expense['monthly_total']
        yearly_expense_total += total

    retain_earning = yearly_income_total - yearly_expense_total

    Liability.objects.create(
        name='Retain Earning',
        description=f'Retain earning for year {year-1}',
        balance=retain_earning,
        year=year
    )

    return retain_earning

def close_loan_repayment(year):
    loans = Loan.objects.filter(start_date__year=year-1)
    total = 0
    for loan in loans:
        total_balance = loan.amount + (loan.amount * loan.interest / 100)
        total += total_balance
        loan_payments = LoanPayment.objects.filter(loan=loan, payment_date__year=year-1).aggregate(total=Sum('amount')).get('total', 0) or 0
        total -= loan_payments

    return total


def close_savings(year):
    # Get total savings for the year using aggregation
    total_amount = SavingsPayment.objects.filter(payment_date__year=year-1).aggregate(total_amount=Sum('amount'))['total_amount']
    
    return total_amount if total_amount else 0


def close_expense(year):
    expenses = Expense.objects.filter(year=year-1)
    new_expenses = []
    expense_payment_updates = []

    for expense in expenses:
        new_expense = Expense(
            name=expense.name,
            expense_type=expense.expense_type,
            description=expense.description,
            balance=0,
            balance_bf=0,
            year=year
        )
        new_expenses.append(new_expense)

    # Bulk create new expenses
    Expense.objects.bulk_create(new_expenses)

    # Create a mapping of old expense to new expense
    expense_mapping = {expense.name: new_expense for expense, new_expense in zip(expenses, new_expenses)}

    # Collect all expense payments that need to be updated
    for expense in expenses:
        expense_payments = ExpensePayment.objects.filter(expense=expense, payment_date__year=year)
        for payment in expense_payments:
            payment.expense = expense_mapping[expense.name]
            expense_payment_updates.append(payment)
            expense.balance -= payment.amount
            expense.save()
            expense_1 = expense_mapping[expense.name]
            expense_1.balance += payment.amount
            expense_1.save()

    # Bulk update expense payments
    ExpensePayment.objects.bulk_update(expense_payment_updates, ['expense'])


def close_income(year):
    incomes = Income.objects.filter(year=year-1)
    new_incomes = []
    income_payments_updates = []

    # Create a mapping of old income to new income
    income_mapping = {}

    for income in incomes:
        new_income = Income(
            name=income.name,
            description=income.description,
            balance=0,
            balance_bf=0,
            year=year
        )
        new_incomes.append(new_income)
        income_mapping[income.id] = new_income

    # Bulk create new incomes
    Income.objects.bulk_create(new_incomes)

    # Collect all income payments that need to be updated
    for income in incomes:
        income_payments = IncomePayment.objects.filter(income=income, payment_date__year=year)
        for payment in income_payments:
            payment.income = income_mapping[income.id]
            income_payments_updates.append(payment)
            income.balance -= payment.amount
            income.save()
            income_1 = income_mapping[income.id]
            income_1.balance += payment.amount
            income_1.save()


    # Bulk update income payments
    IncomePayment.objects.bulk_update(income_payments_updates, ['income'])


def close_liability(year):
    liabilities = Liability.objects.filter(year=year-1)
    new_liabilities = []
    liability_payments_updates = []

    # Create a mapping of old liability to new liability
    liability_mapping = {}

    for liability in liabilities:
        new_liability = Liability(
            name=liability.name,
            balance=liability.balance,
            balance_bf=liability.balance,
            description=liability.description,
            year=year
        )
        new_liabilities.append(new_liability)
        liability_mapping[liability.id] = new_liability

    # Use transaction to ensure atomicity
    with transaction.atomic():
        # Bulk create new liabilities if there are any
        if new_liabilities:
            Liability.objects.bulk_create(new_liabilities)

        # Collect all liability payments that need to be updated
        for liability in liabilities:
            liability_payments = LiabilityPayment.objects.filter(liability=liability, payment_date__year=year)
            liability.balance -= liability_payments.aggregate(total=Sum('amount')).get('total', 0) or 0
            liability.save()
            new_liabilities_1 = liability_mapping[liability.id]
            new_liabilities_1.balance_bf = liability.balance
            new_liabilities_1.balance = liability.balance
            for payment in liability_payments:
                payment.liability = liability_mapping[liability.id]
                liability_payments_updates.append(payment)
                new_liabilities_1.balance += payment.amount
                new_liabilities_1.save()

        # Bulk update liability payments if there are any
        if liability_payments_updates:
            LiabilityPayment.objects.bulk_update(liability_payments_updates, ['liability'])
                  
def close_bank(year):

    banks = Bank.objects.filter(year=year-1)
    new_banks = []
    bank_payments_updates = []

    bank_mapping = {}

    for bank in banks:
        # create a new bank with the same name and balance bf
        new_bank =  Bank(
            name=bank.name,
            balance=bank.balance,
            balance_bf=bank.balance,
            description=bank.description,
            year=year
        )
        new_banks.append(new_bank)
        bank_mapping[bank.id] = new_bank

    # Use transaction to ensure atomicity
    with transaction.atomic():
        # Bulk create new banks if there are any
        if new_banks:
            Bank.objects.bulk_create(new_banks)

        # Collect all bank payments that need to be updated
        for bank in banks:
            bank_payments = BankPayment.objects.filter(bank=bank, payment_date__year=year)
            bank.balance -= bank_payments.aggregate(total=Sum('amount')).get('total', 0) or 0
            bank.save()
            new_bank = bank_mapping[bank.id]
            new_bank.balance_bf = bank.balance
            new_bank.balance = bank.balance
            for payment in bank_payments:
                payment.bank = bank_mapping[bank.id]
                bank_payments_updates.append(payment)
                new_bank.balance += payment.amount
                new_bank.save()

        # Bulk update bank payments if there are any
        if bank_payments_updates:
            BankPayment.objects.bulk_update(bank_payments_updates, ['bank'])


def close_year():

    new_year = Year.current_year() + 1
    new_year_model = Year.objects.create(year=new_year)
    close_bank(year=new_year)

    loan = close_loan_repayment(year=new_year)
    savings = close_savings(year=new_year)
    

    close_expense(year=new_year)
    close_income(year=new_year)
    close_liability(year=new_year)
    retained_earnings = close_profit_and_loss(year=new_year)
    year_end_entry = YearEndEntry.objects.create(year=new_year_model, retained_earnings=retained_earnings, total_loans=loan, total_savings=savings)
    year_end_entry.save()

    verify_trial_balance()

    return year_end_entry

def get_retained_earnings(year):
    return YearEndEntry.objects.get(year=year).retained_earnings