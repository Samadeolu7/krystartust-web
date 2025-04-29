from django import forms
from django.db import transaction
from django_select2.forms import Select2Widget

from user.models import User
from .models import Salary, Tickets, TicketUpdates, Office
from administration.utils import validate_month_status
from main.utils import verify_trial_balance


class PaymentDateValidationMixin(forms.Form):
    def clean(self):
        if 'clean' in self.__class__.__dict__:
            raise RuntimeError("Do not override the `clean` method directly. Use `super().clean()` to extend functionality.")
        cleaned_data = super().clean()
        payment_date = cleaned_data.get('payment_date')
        if payment_date:
            try:
                validate_month_status(payment_date)
            except Exception as e:
                self.add_error('payment_date', str(e))
        return cleaned_data

class VerifyTrialBalanceMixin:
    def save(self, commit=True):
        # Call the parent class's save method
        instance = super().save(commit=commit)

        # Call the post-save hook
        if commit:
            self._post_save_action()
        print("Instance verified")

        return instance

    def _post_save_action(self):
        """
        Hook to perform actions after saving the instance.
        Ensures trial balance verification is executed.
        """
        def safe_verify_trial_balance():
            try:
                verify_trial_balance()
            except Exception as e:
                # Log the exception for debugging purposes
                print(f"Error during trial balance verification: {e}")
                # Optionally, you can log this using Django's logging framework
                # logger.error(f"Error during trial balance verification: {e}")
    
        transaction.on_commit(safe_verify_trial_balance)
    
class BaseValidatedForm(PaymentDateValidationMixin, VerifyTrialBalanceMixin, forms.ModelForm):
    """
    A base form that enforces payment date validation and trial balance verification.
    """
    pass


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
        widgets = { 'client': Select2Widget, }

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

class OfficeForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = '__all__'