from datetime import timezone

from celery import shared_task

from administration.models import Approval, Salary, Transaction
from user.pdf_gen import generate_payslip
from .models import User
from expenses.models import Expense, ExpensePayment
from bank.utils import get_bank_account, create_bank_payment

from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

def get_users_salary(user):
    salaries = Salary.objects.filter(user=user).first()
    total_salary = user.salary + salaries.transportation + salaries.food + salaries.house_rent + salaries.utility + salaries.entertainment + salaries.leave
    return total_salary
    
def record_salary_expense(user):
    salary = get_users_salary(user)
    description = f'Salary Payment for {user.username}'
    expense = Expense.objects.get(name="Payroll Related Expenses")
    last_payment = ExpensePayment.objects.filter(
        expense=expense,
        description=description,
        payment_date__year=timezone.now().year,
        payment_date__month=timezone.now().month
    ).exists()
    
    if last_payment:
        print("Salary expense for this month has already been recorded.")
        return None
      
    tran = Transaction(description="Salary Payment")
    bank = get_bank_account()
    tran.save(prefix='EXP') 
    expense_payment = ExpensePayment.objects.create(expense=expense, amount=salary, description=description, payment_date=timezone.now(), transaction=tran, created_by=user, balance=expense.balance, bank=bank)


    approval = Approval.objects.create(
        type=Approval.Salary,
        content_object=expense_payment,
        content_type=ContentType.objects.get_for_model(ExpensePayment),
        user=user,
        object_id=expense.id,
        comment=description,
    )
    return expense_payment

import logging

logger = logging.getLogger(__name__)

@shared_task
def schedule():
    logger.info("Starting schedule task")
    users = User.objects.all()
    for user in users:
        logger.info(f"Processing user: {user.username}")
        record_salary_expense(user)
    logger.info("Finished schedule task")
    return True


def schedule_task():
    schedule_task = PeriodicTask.objects.filter(name='schedule_task').first()
    if not schedule_task:
        # Create the schedule if it doesn't exist
        crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='59',
            hour='23',
            day_of_month='26',
            month_of_year='*',
            day_of_week='*'
        )
        PeriodicTask.objects.create(
            crontab=crontab_schedule,
            name='schedule_task',
            task='user.tasks.schedule_salary_expense'
        )
    else:
        # Ensure it's enabled
        schedule_task.enabled = True
        schedule_task.save()
    return schedule_task
