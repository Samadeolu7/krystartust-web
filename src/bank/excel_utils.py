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
    payments = BankPayment.objects.filter(bank=bank).select_related('transaction').order_by('payment_date', 'created_at')
    df = pd.DataFrame(list(payments.values('bank__name', 'payment_date','transaction__reference_number', 'amount', 'bank_balance')))
    df.columns = ['Bank', 'Payment Date', 'Reference Number', 'Amount', 'Bank Balance']

    return df

