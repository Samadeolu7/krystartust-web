from django.contrib import admin

from .models import Loan, LoanPayment, LoanRepaymentSchedule

# Register your models here.

admin.site.register(Loan)
admin.site.register(LoanPayment)
admin.site.register(LoanRepaymentSchedule)