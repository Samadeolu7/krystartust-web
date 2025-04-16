from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError

from user.models import Attendance
from user.utils import is_within_allowed_area


@receiver(user_logged_in)
def mark_user_attendance(sender, request, user, **kwargs):
    # Extract latitude and longitude from the request
    # Assuming latitude and longitude are sent in the POST request
    # For example, you can send them as part of the login form
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    # Validate that latitude and longitude are provided
    if not latitude or not longitude:
        messages.error(request, "Invalid location data: Latitude and Longitude are required.")
        return  # Exit early if location data is missing

    # Validate that latitude and longitude are numeric
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        messages.error(request, "Invalid location data: Latitude and Longitude must be numeric.")
        return  # Exit early if location data is not numeric

    # Default location if lat/lng is not provided
    location = 'Default Office'

    try:
        office_location = (6.784626810409781, 3.418928881000768)  # Replace with your office coordinates
        if not is_within_allowed_area(latitude, longitude, office_location):
            # Exit early if the user is not within the allowed area
            messages.error(request, "You are not within the allowed area for attendance.")
            return
        location = f"POINT({longitude} {latitude})"
    except (ValueError, ValidationError) as e:
        # Exit early if there is an error with the location data
        messages.error(request, f"Invalid location data: {e}")
        return

    today = timezone.now().date()

    with transaction.atomic():
        attendance, created = Attendance.objects.select_for_update().get_or_create(user=user, date=today)

    if not attendance.check_in:
        attendance.check_in = timezone.now()
        attendance.location = location
        attendance.save()