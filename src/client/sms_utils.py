import requests
import os
from pathlib import Path
import environ

# # Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(r'D:\Users\User\Desktop\krystartust web\.env')

api_key = env('SMS_API_KEY')


def send_bulk_sms( sender, recipients, message):
    url = 'https://app.smartsmssolutions.com/io/api/client/v1/sms/'
    payload = {
        'token': api_key,
        'sender': sender,
        'to': ','.join(recipients),  # List of phone numbers separated by commas
        'message': message,
        'type': 0  # 0 for standard, 1 for voice, etc.
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Messages sent successfully!")
        print(response.json())
    else:
        print(f"Failed to send SMS. Status code: {response.status_code}")
        print(response.json())

# Example usage
