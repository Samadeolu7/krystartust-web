# management/commands/find_entry.py

from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Find any entry with Dupe in its description'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
        eight_days_ago = today - timedelta(days=8)
        start_of_eight_days_ago = timezone.make_aware(timezone.datetime.combine(eight_days_ago, timezone.datetime.min.time()))

        # Get all the models from the installed apps
        models = apps.get_models()

        # Loop through all the models
        for model in models:
            # Check if the model has a field named 'amount' and 'created_at'
            if hasattr(model, 'amount') and hasattr(model, 'created_at'):
                # Get all the objects created in the last 4 days
                entries = model.objects.filter(created_at__gte=start_of_eight_days_ago, created_at__lte=end_of_day)
                # Loop through all the entries
                for entry in entries:
                    # Check if the entry has a description containing 'Dupe'
                    if hasattr(entry, 'description') and 'Dupe' in entry.description:
                        print(f'{model.__name__} - {entry.created_at} - {entry.description} - {entry.amount} - {entry.id}')

        print('Done')