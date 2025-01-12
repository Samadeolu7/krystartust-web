from bank.models import Bank
from expenses.models import Expense, ExpensePayment
from income.models import Income, IncomePayment
from liability.models import Liability, LiabilityPayment
from loan.models import Loan, LoanPayment
from main.models import Year, YearEndEntry
from savings.models import Savings, SavingsPayment

from django.db.models import Sum


def verify_trial_balance():

    # Aggregate sums in a single query for each model
    total_incomes = Income.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_expenses = Expense.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_savings = Savings.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_loans = Loan.objects.filter(approved=True).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_banks = Bank.objects.aggregate(total=Sum('balance')).get('total', 0) or 0
    total_liability = Liability.objects.aggregate(total=Sum('balance')).get('total', 0) or 0

    # Calculate total credit and debit
    total_credit = total_incomes + total_savings + total_liability
    total_debit = total_expenses + total_loans + total_banks 

    if total_credit == total_debit:
        return True
    else:
        raise ValueError(f'Trial balance does not match. Credit: {total_credit}, Debit: {total_debit}')

def close_trial_balance(year):
    pass


def close_balance_sheet(year):
    pass

def close_profit_and_loss(year):

    incomes_by_month = IncomePayment.objects.filter(created_at__year=year).values(
        'payment_date__month', 'income__name'
    ).annotate(monthly_total=Sum('amount'))

    expenses_by_month = ExpensePayment.objects.filter(payment_date__year=year).values(
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
        decription=f'Retain earning for the year {year}',
        balance=retain_earning,
        year=year+1
    )

    return retain_earning

def close_loan_repayment(year):
    total = Loan.objects.filter(approved=True, start_date__year=year).aggregate(total=Sum('balance')).get('total', 0) or 0
    total_paid = LoanPayment.objects.filter(payment_date__year=year+1).aggregate(total=Sum('amount')).get('total', 0) or 0
    total = total - total_paid
    return total

def close_savings(year):
    # Get total savings for the year using aggregation
    total_amount = SavingsPayment.objects.filter(payment_date__year=year).aggregate(total_amount=Sum('amount'))['total_amount']
    
    return total_amount if total_amount else 0


def close_expense(year):
    expenses = Expense.objects.all()
    new_expenses = []
    expense_payment_updates = []

    for expense in expenses:
        new_expense = Expense(
            name=expense.name,
            balance=expense.balance,
            balance_bf=expense.balance,
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

    # Bulk update expense payments
    ExpensePayment.objects.bulk_update(expense_payment_updates, ['expense'])
     

def close_income(year):
    incomes = Income.objects.all()
    new_incomes = []
    income_payments_updates = []

    for income in incomes:
        new_income = Income.objects.create(
            name=income.name,
            balance=income.balance,
            balance_bf=income.balance,
            year=year
        )

        new_incomes.append(new_income)

    Income.objects.bulk_create(new_incomes)

    income_mapping = {income.name: new_income for income, new_income in zip(incomes, new_incomes)}

    for income in incomes:
        income_payments = IncomePayment.objects.filter(income=income, payment_date__year=year)
        for payment in income_payments:
            payment.income = income_mapping[income.name]
            income_payments_updates.append(payment)  

    IncomePayment.objects.bulk_update(income_payments_updates, ['income'])

def close_liability(year):
    liabilities = Liability.objects.all()
    new_liabilities = []
    liability_payments_updates = []

    for liability in liabilities:
        new_liability = Liability.objects.create(
            name=liability.name,
            balance=liability.balance,
            balance_bf=liability.balance,
            year=year
        )

        new_liabilities.append(new_liability)

    Liability.objects.bulk_create(new_liabilities)

    liability_mapping = {liability.name: new_liability for liability, new_liability in zip(liabilities, new_liabilities)}

    for liability in liabilities:
        liability_payments = LiabilityPayment.objects.filter(liability=liability, payment_date__year=year)
        for payment in liability_payments:
            payment.liability = liability_mapping[liability.name]
            liability_payments_updates.append(payment)

    LiabilityPayment.objects.bulk_update(liability_payments_updates, ['liability'])


def close_bank(year):
    # create all the currents bank again with new year and balance bf

    # get all the banks
    banks = Bank.objects.all()
    for bank in banks:
        # create a new bank with the same name and balance bf
        new_bank =  Bank.objects.create(
            name=bank.name,
            balance=bank.balance,
            balance_bf=bank.balance,
            year=year
        )

        # close the current bank
        bank.save()

def close_year():
    new_year = Year.current_year() + 1
    Year.objects.create(year=new_year)
    close_bank(year=new_year)

    loan = close_loan_repayment(year=new_year)
    savings = close_savings(year=new_year)
    year_end_entry = YearEndEntry.objects.create(year=new_year, loan=loan, savings=savings)
    year_end_entry.save()

    close_expense(year=new_year)
    close_income(year=new_year)
    close_liability(year=new_year)
    verify_trial_balance()