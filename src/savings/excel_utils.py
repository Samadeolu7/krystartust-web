import pandas as pd
from .models import Savings
from .utils import create_savings_payment

def read_excel(file_path):
    return pd.read_excel(file_path)

def savings_from_excel(file_path):
    df = read_excel(file_path)
    for index, row in df.iterrows():
        client_name = row['Client Name']
        amount = row['Amount']
        date = row['Date']
        create_savings_payment(client_name, amount, date)
    return Savings.objects.all()