# client/models.py
from functools import cached_property
from django.db import models
from django.apps import apps

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    group = models.ForeignKey('main.ClientGroup', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @cached_property
    def savings(self):
        return self.savings_set.first()

    @cached_property
    def loan(self):
        return self.loan_set.first()