from datetime import datetime
from django.db.models import Count
from loan.models import Loan

from django.db import transaction, connection

def generate_reference_number(model_class):
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Derive the prefix from the model class name
    prefix = model_class.__name__[:2].upper()

    with transaction.atomic():
        # Lock the rows being counted to prevent race conditions
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM {model_class._meta.db_table} WHERE EXTRACT(YEAR FROM created_at) = %s AND EXTRACT(MONTH FROM created_at) = %s FOR UPDATE",
                [current_year, current_month]
            )
            count = cursor.fetchone()[0] + 1

        # Format the reference number
        reference_number = f"{prefix}-{count:04d}{current_month:02d}{current_year}"
        return reference_number