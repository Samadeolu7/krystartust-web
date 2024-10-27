from django.core.management.base import BaseCommand
from user.pdf_gen import generate_payslip
from user.scheduled import schedule, schedule_task

class Command(BaseCommand):
    help = 'Generate payslips for testing purposes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating payslip PDFs...")
        try:
            result = schedule()
            if result:
                self.stdout.write(self.style.SUCCESS("Payslip PDFs generated successfully."))
            else:
                self.stdout.write(self.style.WARNING("No payslip PDFs generated."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
