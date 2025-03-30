from .models import MonthStatus
from main.utils import verify_trial_balance

from django.db import transaction
from django.contrib import messages
from functools import wraps


def validate_month_status(payment_date):
    month = payment_date.month
    year = payment_date.year

    month_status = MonthStatus.objects.get_or_create(month=month, year=year)[0]
    if month_status.is_closed:
        raise Exception("The month is closed for transactions.")
    

def validate_and_verify(view_func):
    """
    Decorator to validate month status before processing and verify trial balance after processing.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Wrap the view logic in a transaction to ensure atomicity
        with transaction.atomic():
            # Extract the form from the request if it exists
            form = None
            if request.method == 'POST':
                form = kwargs.get('form') or request.POST.get('form')

            # Validate month status if the form has a 'payment_date' field
            if form and hasattr(form, 'cleaned_data') and 'payment_date' in form.cleaned_data:
                try:
                    payment_date = form.cleaned_data['payment_date']
                    validate_month_status(payment_date)
                except Exception as e:
                    messages.error(request, str(e))
                    return view_func(request, *args, **kwargs)  # Return the view with the error

            # Call the original view
            response = view_func(request, *args, **kwargs)

            # Verify trial balance after the view logic
            verify_trial_balance()

            return response

    return wrapper