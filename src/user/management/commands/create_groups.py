# from django.core.management.base import BaseCommand
# from user.pdf_gen import generate_payslip  # Make sure to adjust this import path to your utils module

# class Command(BaseCommand):
#     help = 'Generate payslips for testing purposes'

#     def handle(self, *args, **kwargs):
#         self.stdout.write("Generating payslip PDFs...")
#         try:
#             result = generate_payslip()
#             if result:
#                 self.stdout.write(self.style.SUCCESS("Payslip PDFs generated successfully."))
#             else:
#                 self.stdout.write(self.style.WARNING("No payslip PDFs generated."))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
