import os
from django.template.loader import render_to_string, get_template
from weasyprint import HTML, CSS, default_url_fetcher
from django.conf import settings
from django.utils import timezone
import logging
import requests

from .models import User
from administration.models import Notification, Salary

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def custom_url_fetcher(url, timeout=300):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return {
            'string': response.content,
            'mime_type': response.headers['Content-Type'],
        }
    except requests.RequestException as e:
        logging.error(f"Failed to load image at '{url}': {e}")
        return default_url_fetcher(url)

def generate_payslip(user):
    # Query users who need a payslip
    now = timezone.now()
    month_year = now.strftime('%B %Y')
    salary = None
    template_name = 'payslip_template.html'
    
    # Check if the template can be loaded
    try:
        template = get_template(template_name)
        logging.debug(f"Template '{template_name}' loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading template '{template_name}': {e}")
        return False
    

        # Check if the Salary object exists for the user
    try:
        salary = Salary.objects.get(user=user)
    except Salary.DoesNotExist:
        logging.error(f"Salary record does not exist for user '{user.username}'")

        
    # Render HTML to PDF
    context = {
        'user': user,
        'basic_salary': user.salary,
        'month_year': month_year,
        'salary': salary,
        'static_url': settings.STATIC_URL,
        'base_url': settings.BASE_URL,  # Ensure BASE_URL is defined in settings
    }
        
    try:
        html_string = render_to_string(template_name, context)
        html = HTML(string=html_string, base_url=settings.BASE_URL, url_fetcher=custom_url_fetcher)
        
        # Define the output path for the PDF
        output_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = os.path.join(output_dir, f'{user.username}_payslip_{now.strftime("%Y_%m")}.pdf')
        
        # Generate PDF with landscape orientation
        css = CSS(string='@page { size: A4 landscape; margin: 1cm; }')
        html.write_pdf(pdf_path, stylesheets=[css])
        
        Notification.objects.create(
            user=user,
            message="Your payslip is approved and ready for download.",
            payslip_url=pdf_path
        )
        
        logging.debug(f"Payslip for user '{user.username}' generated successfully.")
    except Exception as e:
        logging.error(f"Error generating payslip for user '{user.username}': {e}")
        return False

    
    return True