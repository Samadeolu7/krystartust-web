# management/commands/find_entry.py

from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import datetime, timedelta, timezone as dt_timezone

class Command(BaseCommand):
    help = 'Find any entry created between 2024-11-14 14:43:28.486108+00:00  and 2024-11-14 14:59:22.251625+00:00'
    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        start = datetime(today.year, today.month, 22, 14, 43, 28, 486108, tzinfo=dt_timezone.utc)
        end = datetime(today.year, today.month, today.day, 15, 00, 22, 251625, tzinfo=dt_timezone.utc)


        # Get all the models from the installed apps
        models = apps.get_models()

        # Loop through all the models
        for model in models:
            # Check if the model has a field named 'amount' and 'created_at'
            if hasattr(model, 'amount') and hasattr(model, 'created_at'):
                # Get all the objects created in the last 4 days
                entries = model.objects.filter(created_at__gte=start, created_at__lte=end)
                # Loop through all the entries
                for entry in entries:
                    # Check if the entry has a description containing 'Dupe'
                    if hasattr(entry, 'description'):
                        print(f'{model.__name__} - {entry.created_at} - {entry.description} - {entry.amount} - {entry.id}')
                    elif hasattr(entry, 'client'):
                        print(f'{model.__name__} - {entry.created_at} - {entry.client.name} - {entry.amount} - {entry.id}')
                    else:
                        print(f'{model.__name__} - {entry.created_at} - {entry.amount} - {entry.id}')


        print('Done')