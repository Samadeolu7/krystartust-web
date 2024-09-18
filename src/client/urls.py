from .views import create_client, edit_client, list_clients, individual_report, create_client_excel

from django.urls import path

urlpatterns = [
    path('create/', create_client, name='create_client'),
    path('edit/<int:client_id>/', edit_client, name='edit_client'),
    path('list/', list_clients, name='list_clients'),
    path('individual-report/<int:pk>/', individual_report, name='individual_report'),
    path('create-from-excel/', create_client_excel, name='create_client_excel'),
]