# client/management/commands/generate_client_ids.py
from django.core.management.base import BaseCommand
from client.models import Client, generate_client_id
from loan.models import Loan

class Command(BaseCommand):
    help = 'Generate client IDs for existing clients'

    def handle(self, *args, **kwargs):
        for client in Client.objects.all():
            if client.client_id == "TEMP":
                client.client_id = generate_client_id(client.client_type)
                client.save()
                self.stdout.write(self.style.SUCCESS(f'Generated client ID for {client.name}'))