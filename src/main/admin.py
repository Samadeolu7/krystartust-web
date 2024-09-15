from django.contrib import admin
from .models import ClientGroup as group, Client

# Register your models here.
admin.site.register(group)
admin.site.register(Client)