from datetime import timezone

from administration.models import Transaction
from user.pdf_gen import generate_payslip
from .models import User
from expenses.models import Expense, ExpensePayment
from bank.utils import get_bank_account, create_bank_payment

from django.db.models import Sum
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

def get_users_salary():
    salaries = User.objects.aggregate(salary=Sum('salary'))
    return salaries['salary']
    
def record_salary_expense():
    salary = get_users_salary()
    expense = Expense.objects.get(name="Payroll Related Expenses")
    last_payment = ExpensePayment.objects.filter(
        expense=expense,
        payment_date__year=timezone.now().year,
        payment_date__month=timezone.now().month
    ).exists()
    
    if last_payment:
        print("Salary expense for this month has already been recorded.")
        return None
    
    transaction = Transaction(description="Salary Payment")
    expense_payment = ExpensePayment.objects.create(expense=expense, amount=salary, description="Salary Payment", payment_date=timezone.now(), transaction=transaction)
    expense_payment.save()
    bank = get_bank_account()
    bank_payment = create_bank_payment(bank, f"Salary Payment for the month of {timezone.now().strftime('%B')}", salary, timezone.now(), transaction, None)
    return expense_payment

def generate_payslip_f():
    
    return generate_payslip()

def schedule():
    record_salary_expense()
    generate_payslip_f()
    return True


def schedule_task():
    schedule_task = PeriodicTask.objects.filter(name='schedule_task').first()
    if not schedule_task:
        # Create the schedule if it doesn't exist
        crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='59',
            hour='23',
            day_of_month='last',
            month_of_year='*',
            day_of_week='*'
        )
        PeriodicTask.objects.create(
            crontab=crontab_schedule,
            name='schedule_task',
            task='user.scheduled.record_salary_expense_task'
        )
    else:
        # Ensure it's enabled
        schedule_task.enabled = True
        schedule_task.save()
    return schedule_task
