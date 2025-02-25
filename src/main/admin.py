from django.contrib import admin
from .models import ClientGroup as group, JournalEntry

# Register your models here.
admin.site.register(group)
admin.site.register(JournalEntry)
