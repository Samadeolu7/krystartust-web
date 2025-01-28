# views.py

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from administration.decorators import allowed_users
from administration.models import Salary
from user.scheduled import record_salary_expense
from .forms import CustomUserCreationForm, CustomUserChangeForm, PasswordChangeForm
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash


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