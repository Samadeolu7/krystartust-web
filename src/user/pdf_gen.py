import os
from django.template.loader import render_to_string, get_template
from weasyprint import HTML
from django.conf import settings
from django.utils import timezone
import logging

from .models import User

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_payslip():
    # Query users who need a payslip
    users = User.objects.all()
    now = timezone.now()
    month_year = now.strftime('%B %Y')
    
    template_name = 'payslip_template.html'
    
    # Check if the template can be loaded
    try:
        template = get_template(template_name)
        logging.debug(f"Template '{template_name}' loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading template '{template_name}': {e}")
        return False
    
    for user in users:
        # Render HTML to PDF
        context = {
            'user': user,
            'salary': user.salary,
            'month_year': month_year,
        }
        
        try:
            html_string = render_to_string(template_name, context)
            html = HTML(string=html_string)
            
            # Define the output path for the PDF
            output_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
            os.makedirs(output_dir, exist_ok=True)
            pdf_path = os.path.join(output_dir, f'{user.username}_payslip_{now.strftime("%Y_%m")}.pdf')
            
            # Generate PDF
            html.write_pdf(pdf_path)
            
            # Here you could also store the PDF path in the user's model or another database model for reference
            user.payslip_url = pdf_path
            user.save()
            
            logging.debug(f"Payslip for user '{user.username}' generated successfully.")
        except Exception as e:
            logging.error(f"Error generating payslip for user '{user.username}': {e}")
            continue
    
    return True