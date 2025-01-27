from django import forms


from user.models import User
from .models import Salary, Approval, Tickets, TicketUpdates


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'

ALL_USERS_OPTION = -1

class UserChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [(ALL_USERS_OPTION, 'All Staff')] + list(self.choices)

    def to_python(self, value):
        if value == str(ALL_USERS_OPTION):
            return ALL_USERS_OPTION
        return super().to_python(value)

class TicketForm(forms.ModelForm):
    class Meta:
        model = Tickets
        fields = ['users', 'client', 'title', 'description', 'priority']

    users = UserChoiceField(
        queryset=User.objects.all(),
        empty_label=None,
        label="Assign to",
        widget=forms.Select,
    )

    def clean_users(self):
        user = self.cleaned_data['users']
        if user == ALL_USERS_OPTION:
            return User.objects.all()
        return [user]

class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = TicketUpdates
        fields = ['message']

    def save(self, commit=True):
        ticket_update = super().save(commit=False)
        if commit:
            ticket_update.save()
        return ticket_update
    

class TicketReassignForm(forms.ModelForm):
    new_user = forms.ModelChoiceField(queryset=User.objects.all(), label="Reassign to")

    class Meta:
        model = Tickets
        fields = ['new_user']