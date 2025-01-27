from django.contrib import admin

from .models import Approval, Salary, Notification, Transaction, Tickets

# Register your models here.
admin.site.register(Approval)
admin.site.register(Salary)
admin.site.register(Notification)
admin.site.register(Transaction)
admin.site.register(Tickets)

