
from datetime import datetime
from django.db import transaction

from bank.utils import create_bank_payment
from main.utils import verify_trial_balance


def approve_expense(approval, user):
    with transaction.atomic():
        approval.approved = True
        approval.approved_by = user
        approval.save()
        expense_payment = approval.content_object
        expense_payment.balance = expense_payment.expense.balance
        expense_payment.expense.balance += expense_payment.amount
        expense_payment.update_at = datetime.now()
        expense_payment.expense.save()
        create_bank_payment(expense_payment.bank, f'expense for {expense_payment.expense}', -expense_payment.amount, datetime.now(), expense_payment.transaction, user)
        verify_trial_balance()

    return True