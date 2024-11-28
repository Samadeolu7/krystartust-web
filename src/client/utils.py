# client/utils.py
from .models import Client

def generate_client_id(client_type):
    """Generate a unique client ID based on the client type."""
    prefix = {
        'WL': 'WL',
        'ML': 'ML',
        'DC': 'DC'
    }.get(client_type, 'CLI')

    last_client = Client.objects.filter(client_type=client_type, client_id__startswith=prefix).order_by('client_id').last()
    if not last_client:
        return f'{prefix}0001'
    
    try:
        last_id = int(last_client.client_id[len(prefix):])
    except ValueError:
        # Handle cases where the client_id does not follow the expected format
        last_id = 0
    
    new_id = last_id + 1
    return f'{prefix}{new_id:04d}'