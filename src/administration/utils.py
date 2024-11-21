from .models import MonthStatus

from django.db import transaction, connection


def validate_month_status(payment_date):
    month = payment_date.month
    year = payment_date.year

    month_status = MonthStatus.objects.get_or_create(month=month, year=year)[0]
    if month_status.is_closed:
        raise Exception("The month is closed for transactions.")
    