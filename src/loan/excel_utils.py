import pandas as pd
from .utils import create_loan_payment

def read_excel(file_path):
    return pd.read_excel(file_path)

def loan_from_excel(file_path):
    df = read_excel(file_path)
    for index, row in df.iterrows():
        client_name = row['Client Name']
        amount = row['Amount']
        create_loan_payment(client_name, amount)