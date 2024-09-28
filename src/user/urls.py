# urls.py

from django.urls import path
from .views import add_user, user_list

urlpatterns = [
    path('add-user/', add_user, name='add_user'),
    path('user-list/', user_list, name='list_users'),
    # Add other URL patterns here
]