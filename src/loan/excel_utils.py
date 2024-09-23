import csv
import pandas as pd
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone  # Import timezone module
from bank.utils import create_bank_payment, get_bank_account
from client.models import Client
from income.utils import create_loan_interest_income_payment, create_risk_premium_income_payment, create_union_contribution_income_payment
from .models import Loan, LoanRepaymentSchedule
from .utils import create_loan_payment
from income.models import LoanServiceFee, RiskPremium

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def read_excel(file_path):
    return pd.read_excel(file_path)

from dateutil.parser import parse

def parse_date(date_str, dayfirst=True, yearfirst=False):
    try:
        return parse(date_str, dayfirst=dayfirst, yearfirst=yearfirst)
    except ValueError:
        raise ValueError(f"Date format for '{date_str}' is not supported")

def bulk_create_loans_from_excel(file_path):
    df = read_excel(file_path)
    report_rows = []

    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                # Extract data from the row
                client_name = row['Name']
                amount = Decimal(row['Amount'])
                interest = LoanServiceFee.load().amount
                duration = 23
                date_str = str(row['Date'])
                start_date = pd.to_datetime(date_str, dayfirst=False, errors='coerce')
                
                # Ensure start_date is a datetime object
                if pd.isnull(start_date):
                    raise ValueError(f"Unsupported date format for '{row['Date']}'")

                # Make the datetime object timezone-aware
                start_date = timezone.make_aware(start_date, timezone.get_current_timezone())

                loan_type = 'Weekly'
                risk_premium = RiskPremium.load().amount

                # Create Loan instance
                loan = Loan(
                    client=Client.objects.get(name=client_name),
                    amount=amount,
                    interest=interest,
                    duration=duration,
                    start_date=start_date,
                    loan_type=loan_type,
                    risk_premium=risk_premium,
                    balance=amount * (Decimal(1) + (interest / Decimal(100))),
                    end_date=start_date + timedelta(days=duration) + timedelta(weeks=1),
                    emi=(amount * (Decimal(1) + (interest / Decimal(100)))) / duration,
                    status='Active'
                )
                loan.save()

                # Determine the increment based on loan type
                time_increment = {
                    'Daily': timedelta(days=1),
                    'Weekly': timedelta(weeks=1),
                    # Add more loan types as needed
                }.get(loan_type, timedelta(weeks=1))  # Default to weekly if the loan type is not specifically listed

                # Create repayment schedule based on the loan type and duration
                amount_due = loan.balance / duration
                for i in range(duration):
                    due_date = start_date + timedelta(weeks=1) + (i * time_increment)  # Start 1 week after the start date

                    LoanRepaymentSchedule.objects.create(
                        loan=loan,
                        due_date=due_date,
                        amount_due=amount_due,
                    )

                # Subtract loan amount from bank balance
                create_bank_payment(
                    bank=get_bank_account(),
                    description=f'Loan disbursement to {loan.client.name}',
                    amount=-amount,
                    payment_date=start_date,
                )

                # Create interest income payment
                interest_amount = interest * amount / Decimal(100)
                create_loan_interest_income_payment(interest_amount, start_date)

                # Create risk premium payment
                risk_premium_amount = risk_premium * amount / Decimal(100)
                create_risk_premium_income_payment(risk_premium_amount, start_date)

                # Create union contribution payment
                create_union_contribution_income_payment(start_date)

                report_rows.append([client_name, "success", "Loan and associated records created successfully"])
                
            except Exception as e:
                logging.error(f"Error processing row {index} for client {client_name}: {e}")
                report_rows.append([client_name, "failed", str(e)])

    # Write the report
    report_path = 'loan_creation_report.csv'
    with open(report_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Client Name', 'Status', 'Message'])  # Header row
        writer.writerows(report_rows)

    # Return the CSV file path
    return report_path
import csv
from io import StringIO

def loan_from_excel(file):
    df = read_excel(file)
    report_rows = []

    for index, row in df.iterrows():
        try:
            client_name = row['Name']
            amount = row['Amount']
            date_str = str(row['Date'])
            date = pd.to_datetime(date_str, dayfirst=True, errors='coerce')
            
            # Ensure date is a datetime object
            if pd.isnull(date):
                raise ValueError(f"Unsupported date format for '{row['Date']}'")

            # Make the datetime object timezone-aware
            date = timezone.make_aware(date, timezone.get_current_timezone())

            client = Client.objects.get(name=client_name)
            loan = Loan.objects.get(client=client)
            create_loan_payment(client, loan, amount, date)

            report_rows.append([client_name, "success", "Loan payment created successfully"])
        except Exception as e:
            logging.error(f"Error processing row {index} for client {client_name}: {e}")
            report_rows.append([client_name, "failed", str(e)])

    # Create the CSV content
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Client Name', 'Status', 'Message'])  # Header row
    writer.writerows(report_rows)

    # Return the CSV content
    return output.getvalue()