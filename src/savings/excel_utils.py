import csv
import pandas as pd
import logging
from django.db import transaction
from client.models import Client
from .models import SavingsPayment
from .utils import create_savings_payment

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def read_excel(file_path):
    return pd.read_excel(file_path)

def savings_from_excel(file_path):
    df = read_excel(file_path)
    report_rows = []

    with transaction.atomic():
        for index, row in df.iterrows():
            client_name = row['Name']
            amount = row['Amount']
            date = row['Date']
            client = Client.objects.filter(name=client_name).first()
            if client:
                try:
                    create_savings_payment(client, amount, date)
                    report_rows.append([client_name, "success", "Savings payment created successfully"])
                except Exception as e:
                    logging.error(f"Error creating savings payment for client {client_name}: {e}")
                    report_rows.append([client_name, "failed", str(e)])
            else:
                logging.error(f"Client with name {client_name} not found.")
                report_rows.append([client_name, "failed", "Client not found"])

    # Write the report
    report_path = 'savings_creation_report.csv'
    with open(report_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Client Name', 'Status', 'Message'])  # Header row
        writer.writerows(report_rows)

    # Return the CSV file path
    return report_path