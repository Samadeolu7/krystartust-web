from django.db import models

from client.models import Client
from user.models import User    

# Create your models here.
class ClientGroup(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Year(models.Model):
    year = models.IntegerField()

    def __str__(self):
        return str(self.year)
    
    @classmethod
    def current_year(cls):
        last_year_instance = cls.objects.order_by('-year').first()
        if last_year_instance:
            return last_year_instance.year
        else:
            return 2024