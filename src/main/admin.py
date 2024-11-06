from django.contrib import admin
from .models import ClientGroup as group, Client, JournalEntry

# Register your models here.
admin.site.register(group)
admin.site.register(Client)
admin.site.register(JournalEntry)
