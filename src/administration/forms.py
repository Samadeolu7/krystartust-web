from django import forms


from user.models import User
from .models import Salary, Approval, Tickets, TicketUpdates


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'



class TicketForm(forms.ModelForm):
    ALL_USERS_OPTION = -1

    class Meta:
        model = Tickets
        fields = ['users', 'client', 'title', 'description', 'priority']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['users'].queryset = User.objects.all()
        self.fields['users'].choices = [('', 'Select User')] + [(self.ALL_USERS_OPTION, 'All Staff')] + list(self.fields['users'].choices)

    def clean_users(self):
        users = self.cleaned_data['users']
        if users and users[0] == self.ALL_USERS_OPTION:
            return User.objects.all()
        return users


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