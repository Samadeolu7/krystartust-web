from user.scheduled import schedule
from celery import shared_task


@shared_task
def schedule_salary_expense():
    schedule()
    return True