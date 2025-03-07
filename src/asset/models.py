from django.urls import reverse
from django.db import models

# Create your models here.

class Asset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset_name
    
    def get_absolute_url(self):
        return reverse('asset_detail', kwargs={'pk': self.pk})
    

class AssetRecord(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset.name

    def get_absolute_url(self):
        return reverse('asset_record_detail', kwargs={'pk': self.pk})