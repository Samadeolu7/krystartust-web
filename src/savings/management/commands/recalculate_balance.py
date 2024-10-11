from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

import pytz
from loan.models import LoanRepaymentSchedule
from django.db import transaction

class Command(BaseCommand):
    help = 'Shift the due date of all LoanRepaymentSchedule entries created before 10-10-2024 by one week'

    def handle(self, *args, **kwargs):
        target_date = timezone.datetime(2024, 10, 10, tzinfo=pytz.UTC)
        one_week = timedelta(weeks=1)

        schedules_to_update = LoanRepaymentSchedule.objects.filter(loan__created_at__lt=target_date)

        with transaction.atomic():
            for schedule in schedules_to_update:
                schedule.due_date += one_week
                schedule.save()

        self.stdout.write(self.style.SUCCESS('Successfully shifted due dates for all relevant LoanRepaymentSchedule entries'))