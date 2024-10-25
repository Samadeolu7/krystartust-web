from django.contrib import admin

from .models import Approval, Salary, Notification

# Register your models here.
admin.site.register(Approval)
admin.site.register(Salary)
admin.site.register(Notification)
