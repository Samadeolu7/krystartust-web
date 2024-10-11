from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'salary', 'is_active', 'is_staff', 'groups', 'user_permissions')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'salary', 'is_active', 'is_staff', 'groups', 'user_permissions')