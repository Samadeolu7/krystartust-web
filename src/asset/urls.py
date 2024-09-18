from django.urls import path
from .views import create_asset

urlpatterns = [
    path('create/', create_asset, name='create_asset'),
]
