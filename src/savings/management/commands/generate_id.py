# client/management/commands/generate_client_ids.py
from django.core.management.base import BaseCommand
from client.models import Client
from client.utils import generate_client_id
from loan.models import Loan

class Command(BaseCommand):
    help = 'Generate client IDs for existing clients'

    def handle(self, *args, **kwargs):
        loans = Loan.objects.filter(client__client_id='TEMP')
        for loan in loans:
            if loan.loan_type == 'Weekly':
                loan.client.client_type = 'WL'
            elif loan.loan_type == 'Monthly':
                loan.client.client_type = 'ML'
            elif loan.loan_type == 'Daily':
                loan.client.client_type = 'DC'
            loan.client.client_id = generate_client_id(loan.client.client_type)
            loan.client.save()
            self.stdout.write(self.style.SUCCESS(f'Generated ID for {loan.client.name}: {loan.client.client_id}'))