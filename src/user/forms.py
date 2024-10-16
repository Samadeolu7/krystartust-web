from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from administration.models import Salary
from django.contrib.auth.models import Group, Permission



class CustomUserCreationForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    position = forms.CharField(max_length=100)
    transportation = forms.DecimalField(max_digits=10, decimal_places=2)
    food = forms.DecimalField(max_digits=10, decimal_places=2)
    house_rent = forms.DecimalField(max_digits=10, decimal_places=2)
    utility = forms.DecimalField(max_digits=10, decimal_places=2)
    entertainment = forms.DecimalField(max_digits=10, decimal_places=2)
    leave = forms.DecimalField(max_digits=10, decimal_places=2)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    user_permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('email', 'username', 'is_active', 'is_staff', 'groups', 'user_permissions', 
                  'department', 'position', 'transportation', 'food', 'house_rent', 'utility', 
                  'entertainment', 'leave')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            self.save_m2m()  # Save the many-to-many data for the form
            Salary.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                position=self.cleaned_data['position'],
                transportation=self.cleaned_data['transportation'],
                food=self.cleaned_data['food'],
                house_rent=self.cleaned_data['house_rent'],
                utility=self.cleaned_data['utility'],
                entertainment=self.cleaned_data['entertainment'],
                leave=self.cleaned_data['leave']
            )
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'salary', 'is_active', 'is_staff', 'groups', 'user_permissions')