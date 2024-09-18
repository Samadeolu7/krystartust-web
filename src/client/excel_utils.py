import pandas as pd
import csv
from client.models import Client
from main.models import ClientGroup as Group
from income.utils import create_id_fee_income_payment, create_registration_fee_income_payment
from savings.utils import create_compulsory_savings

def read_excel(file_path):
    """Read an excel file and return a DataFrame."""
    return pd.read_excel(file_path)

def create_clients_from_excel(file_path):
    """Create clients from an excel file."""
    df = read_excel(file_path)
    report_path = 'client_creation_report.csv'

    with open(report_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Client Name', 'Status', 'Message'])  # Header row

        for index, row in df.iterrows():
            group = Group.objects.get(name=row['Group'])
            try:
                client = Client.objects.create(
                    name=row['Name'],
                    email=row['Email'],
                    phone=row['Phone'],
                    address=row['Address'],
                    group=group,
                    created_at=row['Date']
                )
                client.save()
                create_compulsory_savings(client)
                create_registration_fee_income_payment(client.created_at)
                create_id_fee_income_payment(client.created_at)
                writer.writerow([client.name, "success", "Client created successfully"])
            except Exception as e:
                writer.writerow([row['Name'], "failed", str(e)])
                continue

    # Return the CSV file path
    return report_path