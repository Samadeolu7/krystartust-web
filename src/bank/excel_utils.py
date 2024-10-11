import csv
import pandas as pd
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone  # Import timezone module
from client.models import Client
from .models import Bank, BankPayment

def bank_to_excel(bank):
    payments = BankPayment.objects.filter(bank=bank)
    df = pd.DataFrame(list(payments.values('bank__name', 'payment_date','description', 'amount')))
    df.columns = ['Bank', 'Payment Date', 'Description', 'Amount']

    return df

