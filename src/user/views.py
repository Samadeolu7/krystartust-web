# views.py

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from user.utils import is_within_allowed_area
from .models import Attendance

from administration.decorators import allowed_users
from administration.models import Salary
from user.scheduled import record_salary_expense
from .forms import CustomUserCreationForm, CustomUserChangeForm, PasswordChangeForm
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    def form_valid(self, form):
        #print location data from the request
        latitude = self.request.POST.get('latitude')
        longitude = self.request.POST.get('longitude')
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        # The signal will handle the location data from the POST request
        return super().form_valid(form)


@login_required
def check_in(request):
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    # Validate that latitude and longitude are provided
    if not latitude or not longitude:
        messages.error(request, "Invalid location data: Latitude and Longitude are required.")
        return redirect(reverse('dashboard'))

    # Validate that latitude and longitude are numeric
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        messages.error(request, "Invalid location data: Latitude and Longitude must be numeric.")
        return redirect(reverse('dashboard'))

    # Validate that the user is within the allowed area
    office_location = (12.971598, 77.594566)  # Replace with your office coordinates
    if not is_within_allowed_area(latitude, longitude, office_location):
        messages.error(request, "You are not within the allowed area for attendance.")
        return redirect(reverse('dashboard'))

    # Update or create the attendance record
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(user=request.user, date=today)

    if attendance.check_in:
        messages.error(request, "You have already checked in for today.")
        return redirect(reverse('dashboard'))

    # Update the check-in time and location
    attendance.check_in = timezone.now()
    attendance.location = f"POINT({longitude} {latitude})"
    attendance.save()

    messages.success(request, "You have successfully checked in.")
    return redirect(reverse('dashboard'))

@login_required
def check_out(request):
    today = timezone.now().date()
    attendance = Attendance.objects.filter(user=request.user, date=today).first()

    if not attendance:
        # No attendance record found
        messages.error(request, "No check-in record found for today.")
        return redirect(reverse('dashboard'))

    if attendance.check_out:
        # Already checked out
        messages.error(request, "You have already checked out for today.")
        return redirect(reverse('dashboard'))

    if not attendance.check_in:
        # No check-in time set
        messages.error(request, "You cannot check out without checking in first.")
        return redirect(reverse('dashboard'))

    # Validate location for check-out
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    if not latitude or not longitude:
        messages.error(request, "Invalid location data: Latitude and Longitude are required.")
        return redirect(reverse('dashboard'))

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        messages.error(request, "Invalid location data: Latitude and Longitude must be numeric.")
        return redirect(reverse('dashboard'))

    office_location = (12.971598, 77.594566)  # Replace with your office coordinates
    if not is_within_allowed_area(latitude, longitude, office_location):
        messages.error(request, "You are not within the allowed area for check-out.")
        return redirect(reverse('dashboard'))

    # Update the check-out time
    attendance.check_out = timezone.now()
    attendance.save()
    messages.success(request, "You have successfully checked out.")
    return redirect(reverse('dashboard'))

@login_required
@allowed_users(allowed_roles=['Admin'])
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assign groups to the user
            groups = form.cleaned_data['groups']
            user.groups.set(groups)
            user.save()
            return redirect('user_list')  # Redirect to a user list view or any other view
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/add_user.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin'])
def user_list(request):
    User = get_user_model()
    users = User.objects.all()

    return render(request, 'registration/user_list.html', {'users': users})

@login_required
@allowed_users(allowed_roles=['Admin'])
def user_detail(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    salary = Salary.objects.filter(user=user).first()
    context = {
        'user': user,
        'salary': salary
    }
    return render(request, 'registration/user_detail.html', context)

@login_required
@allowed_users(allowed_roles=['Admin'])
def user_update(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            # Assign groups to the user
            groups = form.cleaned_data['groups']
            user.groups.set(groups)
            user.save()
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'registration/user_update.html', {'form': form})

@login_required
def change_password(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user)
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
@allowed_users(allowed_roles=['Admin'])
def record_salary_expense_view(request):
    users = User.objects.all()
    for user in users:
        record_salary_expense(user)
    
    return JsonResponse({'status': 'success', 'message': 'Salary expense recorded for all users'})