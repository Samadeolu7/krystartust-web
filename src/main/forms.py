# forms.py
from django import forms
from .models import ClientGroup as Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'