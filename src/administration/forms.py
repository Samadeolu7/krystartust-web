from django import forms

from .models import Salary, Approval


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'
