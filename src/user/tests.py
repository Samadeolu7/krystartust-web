from django.db import IntegrityError
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.core.exceptions import ValidationError
from .models import Attendance
from .utils import is_within_allowed_area


class AttendanceTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", username="testuser", password="password123"
        )
        self.office_location = (12.971598, 77.594566)  # Example office coordinates
        self.client = Client()

    def test_mark_attendance_check_in_with_valid_location(self):
        """Test that a user can successfully check in with a valid location."""
        today = now().date()
        response = self.client.post(
            reverse('login'),
            {
                "username": self.user.email,
                "password": "password123",
                "latitude": 12.971598,
                "longitude": 77.594566,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        attendance = Attendance.objects.get(user=self.user, date=today)
        self.assertIsNotNone(attendance.check_in)
        self.assertEqual(str(attendance.location), "POINT(77.594566 12.971598)")

    def test_mark_attendance_check_in_with_invalid_location(self):
        """Test that a user cannot check in with an invalid location."""
        
        response = self.client.post(
            reverse('login'),
            {
                "username": self.user.email,
                "password": "password123",
                "latitude": 13.000000,
                "longitude": 77.000000,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        attendance_exists = Attendance.objects.filter(user=self.user, date=now().date()).exists()
        self.assertFalse(attendance_exists)

    def test_is_within_allowed_area_valid(self):
        """Test that a valid location is within the allowed area."""
        lat, lng = 12.971598, 77.594566  # Same as office location
        self.assertTrue(is_within_allowed_area(lat, lng, self.office_location))

    def test_is_within_allowed_area_invalid(self):
        """Test that an invalid location is outside the allowed area."""
        lat, lng = 13.000000, 77.000000  # Far from office location
        self.assertFalse(is_within_allowed_area(lat, lng, self.office_location))

    
    def test_duplicate_attendance(self):
        """Test that duplicate attendance records for the same user and date are not allowed."""
        today = now().date()
        Attendance.objects.create(user=self.user, date=today, check_in=now())
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(user=self.user, date=today, check_in=now())

    def test_str_representation(self):
        """Test the string representation of the Attendance model."""
        check_in_time = now()
        attendance = Attendance.objects.create(user=self.user, date=now().date(), check_in=check_in_time)
        expected_str = f"Attendance for {self.user} on {attendance.date} (Check-in: {check_in_time}, Check-out: N/A)"
        self.assertEqual(str(attendance), expected_str)

    def test_multiple_check_ins_same_day(self):
        """Test that a user cannot check in multiple times on the same day."""
        today = now().date()
        initial_check_in = now()
        Attendance.objects.create(user=self.user, date=today, check_in=initial_check_in)
    
        response = self.client.post(
            reverse('login'),
            {
                "username": self.user.email,
                "password": "password123",
                "latitude": 12.971598,
                "longitude": 77.594566,
            },
            follow=True,
        )
    
        # Confirm no new attendance record was created
        self.assertEqual(Attendance.objects.filter(user=self.user, date=today).count(), 1)
    
        # Confirm the check-in time was not updated
        attendance = Attendance.objects.get(user=self.user, date=today)
        self.assertEqual(attendance.check_in, initial_check_in)

    def test_check_in_without_location(self):
        """Test that check-in fails if location is not provided."""
        response = self.client.post(
            reverse('login'),
            {
                "username": self.user.email,
                "password": "password123",
                # No latitude or longitude
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        attendance_exists = Attendance.objects.filter(user=self.user, date=now().date()).exists()
        self.assertFalse(attendance_exists)

        # Check for error message
        messages = list(response.context['messages'])
        self.assertTrue(any("Invalid location data" in str(message) for message in messages))

    def test_check_in_with_invalid_lat_lng_format(self):
        """Test that non-numeric lat/lng are handled gracefully."""
        response = self.client.post(
            reverse('login'),
            {
                "username": self.user.email,
                "password": "password123",
                "latitude": "not-a-number",
                "longitude": "77.594566",
            },
            follow=True,
        )
    
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Attendance.objects.filter(user=self.user, date=now().date()).exists())
    
        # Check for error message
        messages = list(response.context['messages'])
        self.assertTrue(any("Invalid location data" in str(message) for message in messages))

    def test_check_out_without_check_in(self):
        """Test that a user cannot check out without first checking in."""
        response = self.client.get(reverse('check_out'), follow=True)
    
        self.assertEqual(response.status_code, 200)
    
        # Check for error message
        messages = list(response.context['messages'])
        self.assertTrue(any("No check-in record found for today" in str(message) for message in messages))

    def test_valid_check_out(self):
        """Test that a user can successfully check out after checking in."""
        today = now().date()
        Attendance.objects.create(user=self.user, date=today, check_in=now())
    
        response = self.client.get(reverse('check_out'), follow=True)
    
        self.assertEqual(response.status_code, 200)
    
        # Check that check-out time is set
        attendance = Attendance.objects.get(user=self.user, date=today)
        self.assertIsNotNone(attendance.check_out)

    def test_duplicate_check_out(self):
        """Test that a user cannot check out multiple times on the same day."""
        today = now().date()
        Attendance.objects.create(user=self.user, date=today, check_in=now(), check_out=now())
    
        response = self.client.get(reverse('check_out'), follow=True)
    
        self.assertEqual(response.status_code, 200)
    
        # Check for error message
        messages = list(response.context['messages'])
        self.assertTrue(any("You have already checked out" in str(message) for message in messages))