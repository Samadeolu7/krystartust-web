# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
from django.contrib.auth import get_user_model


@login_required
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
def user_list(request):
    User = get_user_model()
    users = User.objects.all()

    print(users)
    return render(request, 'registration/user_list.html', {'users': users})

@login_required
def user_detail(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    return render(request, 'registration/user_detail.html', {'user': user})

@login_required
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