from django.contrib import admin
from .models import Savings, SavingsPayment, CompulsorySavings, DailyContribution, ClientContribution

# Register your models here.

admin.site.register(Savings)
admin.site.register(SavingsPayment)
admin.site.register(CompulsorySavings)
admin.site.register(DailyContribution)
admin.site.register(ClientContribution)