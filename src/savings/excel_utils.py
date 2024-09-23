import csv
from datetime import datetime
import pandas as pd
import logging
from django.db import transaction
from django.utils import timezone  # Import timezone module
from client.models import Client
from .models import SavingsPayment
from .utils import create_savings_payment
from loan.excel_utils import parse_date

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def read_excel(file_path):
    return pd.read_excel(file_path)  # Ensure day-first format

def savings_from_excel(file_path):
    df = read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)  # Ensure day-first format
    report_rows = []

    with transaction.atomic():
        for index, row in df.iterrows():
            client_name = row['Name']
            amount = row['Amount']
            date = row['Date']
            client = Client.objects.filter(name=client_name).first()
            if client:
                try:
                    # Ensure date is a datetime object
                    if isinstance(date, str):
                        date = parse_date(date)
                    elif not isinstance(date, datetime):
                        raise ValueError(f"Unsupported date format for '{date}'")

                    # Make the datetime object timezone-aware
                    date = timezone.make_aware(date, timezone.get_current_timezone())

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