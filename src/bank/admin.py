from django.contrib import admin

from .models import Bank, BankPayment
# Register your models here.

admin.site.register(Bank)
admin.site.register(BankPayment)
