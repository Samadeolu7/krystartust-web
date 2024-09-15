from django.contrib import admin
from .models import Savings, SavingsPayment, CompulsorySavings

# Register your models here.

admin.site.register(Savings)
admin.site.register(SavingsPayment)
admin.site.register(CompulsorySavings)