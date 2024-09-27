from django.contrib import admin
from .models import Liability, LiabilityPayment

# Register your models here.

admin.site.register(Liability)
admin.site.register(LiabilityPayment)