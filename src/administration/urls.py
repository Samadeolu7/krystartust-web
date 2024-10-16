from django.urls import path

from .views import salary

urlpatterns = [
    path('salary/', salary, name='salary'),
]