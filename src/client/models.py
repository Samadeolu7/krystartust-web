# client/models.py
from datetime import datetime
from functools import cached_property
from django.db import models
from django.apps import apps

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    next_of_kin = models.CharField(max_length=100, null=True, blank=True)
    next_of_kin_phone = models.CharField(max_length=15, null=True, blank=True)
    group = models.ForeignKey('main.ClientGroup', on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100,null=True, blank=True)
    account_number = models.CharField(max_length=100,null=True, blank=True)
    date = models.DateField( default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @cached_property
    def savings(self):
        return self.savings_set.first()

    @cached_property
    def loan(self):
        return self.loan_set.first()