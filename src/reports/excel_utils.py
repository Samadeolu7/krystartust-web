from datetime import datetime
import pandas as pd
import csv
import logging
from client.models import Client
from loan.models import Loan
from main.models import ClientGroup as Group
from income.utils import create_id_fee_income_payment, create_registration_fee_income_payment
from savings.models import Savings
from savings.utils import create_compulsory_savings
from django.db import transaction
from django.utils import timezone  # Import timezone module
from loan.excel_utils import parse_date


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

