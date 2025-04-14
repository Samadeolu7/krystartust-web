from geopy.distance import distance
from django.conf import settings

def is_within_allowed_area(lat, lng, office_location, threshold=0.5):
    """
    Checks if a given lat/lng is within the allowed radius (in kilometers) of the office location.
    """
    try:
        user_location = (float(lat), float(lng))
        print(f"User location: {user_location}")
        threshold = threshold or getattr(settings, 'ATTENDANCE_RADIUS_KM', 0.5)
        dist = distance(user_location, office_location).km
        return dist <= threshold
    except (ValueError, TypeError):
        print("Invalid latitude or longitude provided.")
        return False