from datetime import datetime
import pandas as pd
import csv
import logging
from client.models import Client
from main.models import ClientGroup as Group
from income.utils import create_id_fee_income_payment, create_registration_fee_income_payment
from savings.utils import create_compulsory_savings
from django.db import transaction
from django.utils import timezone  # Import timezone module
from loan.excel_utils import parse_date

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def read_excel(file_path):
    """Read an excel file and return a DataFrame."""
    return pd.read_excel(file_path)

def create_clients_from_excel(file_path):
    """Create clients from an excel file."""
    df = read_excel(file_path)
    report_path = 'client_creation_report.csv'
    clients_to_create = []
    report_rows = []
    unique_names = set()  # Set to track unique names

    with transaction.atomic():
        for index, row in df.iterrows():
            group, created = Group.objects.get_or_create(name=row['Group'])
            if created:
                group.description = "Description for the new group"  # Add your description here
                group.save()
            try:
                if row['Name'] in unique_names:
                    raise ValueError(f"Duplicate name found: {row['Name']}")
                unique_names.add(row['Name'])

                # Extract and parse the date
                date = row['Date']
                if isinstance(date, pd.Timestamp):
                    date = date.to_pydatetime()
                elif isinstance(date, str):
                    date = parse_date(date)
                else:
                    raise ValueError(f"Unsupported date format for '{date}'")

                # Make the datetime object timezone-aware
                date = timezone.make_aware(date, timezone.get_current_timezone())

                client = Client(
                    name=row['Name'],
                    email=row['Email'],
                    phone=row['Phone'],
                    address=row['Address'],
                    group=group,
                    created_at=date
                )
                clients_to_create.append(client)
                report_rows.append([client.name, "success", "Client created successfully"])
            except Exception as e:
                logging.error(f"Error creating client for row {index}: {e}")
                report_rows.append([row['Name'], "failed", str(e)])
                continue

        try:
            # Bulk create clients
            Client.objects.bulk_create(clients_to_create)

            # Perform post-creation operations
            for client in clients_to_create:
                try:
                    create_compulsory_savings(client)
                    create_registration_fee_income_payment(client.created_at)
                    create_id_fee_income_payment(client.created_at)
                except Exception as e:
                    logging.error(f"Error in post-creation operations for client {client.name}: {e}")
                    report_rows.append([client.name, "partial success", f"Post-creation error: {e}"])
        except Exception as e:
            logging.error(f"Error in bulk creation of clients: {e}")
            for client in clients_to_create:
                report_rows.append([client.name, "failed", f"Bulk creation error: {e}"])

    # Write the report
    with open(report_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Client Name', 'Status', 'Message'])  # Header row
        writer.writerows(report_rows)

    # Return the CSV file path
    return report_path