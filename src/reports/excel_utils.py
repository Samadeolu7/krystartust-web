from datetime import date
import pandas as pd
from loan.models import Loan, LoanPayment, LoanRepaymentSchedule
from savings.models import Savings, SavingsPayment


def client_list_to_excel():
    # Fetch savings and loan data
    savings = Savings.objects.all()
    loans = Loan.objects.all()

    # Create DataFrame for savings
    savings_df = pd.DataFrame(list(savings.values(
        'client__name', 'client__phone', 'client__email', 'client__address', 'client__group__name', 'balance', 'created_at'
    )))
    savings_df.columns = ['Name', 'Phone', 'Email', 'Address', 'Group', 'Savings Balance']

    # Create DataFrame for loans
    loans_df = pd.DataFrame(list(loans.values(
        'client__name', 'balance'
    )))
    loans_df.columns = ['Name', 'Loan Balance']

    # Merge savings and loan DataFrames on the client name
    merged_df = pd.merge(savings_df, loans_df, on='Name', how='left')

    return merged_df

def defaulter_report_to_excel():
    # Fetch savings and loan data
    today = date.today()

    # Fetch the necessary fields from the loan repayment schedule to avoid unnecessary data loading
    overdue_schedules = LoanRepaymentSchedule.objects.filter(
        due_date__lt=today,
        is_paid=False
    ).select_related('loan').only(
        'loan__id', 'loan__client__name', 'loan__client__phone', 'loan__amount', 'loan__balance', 
        'loan__start_date', 'loan__end_date', 'loan__status', 'due_date', 'amount_due', 'is_paid'
    )

    df = pd.DataFrame(list(overdue_schedules.values(
        'loan__client__name', 'loan__client__phone', 'loan__amount', 'loan__balance', 'loan__start_date', 'loan__end_date', 'loan__status', 'due_date', 'amount_due', 'is_paid'
    )))

    df.columns = ['Name', 'Phone', 'Loan Amount', 'Loan Balance', 'Start Date', 'End Date', 'Status', 'Due Date', 'Amount Due', 'Is Paid']

    return df

def client_savings_payments_to_excel(client):
    # Fetch savings and loan data
    savings = SavingsPayment.objects.filter(client=client)
    df = pd.DataFrame(list(savings.values('client__name', 'amount', 'payment_date', 'transaction_type', 'balance')))
    df.columns = ['Name', 'Amount', 'Payment Date', 'Transaction Type', 'Balance']

    return df

def client_loans_payments_to_excel(client):
    # Fetch savings and loan data
    loans = LoanRepaymentSchedule.objects.filter(loan__client=client)
    df = pd.DataFrame(list(loans.values('loan__client__name', 'amount', 'payment_date', 'due_date', 'is_paid')))
    df.columns = ['Name', 'Amount', 'Payment Date', 'Due Date', 'Is Paid']

    return df