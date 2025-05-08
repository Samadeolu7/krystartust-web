from .views import create_client, edit_client, list_clients, individual_report, generate_client_id_view, create_prospect, view_prospects, edit_prospect

from django.urls import path

urlpatterns = [
    path('create/', create_client, name='create_client'),
    path('edit/<int:client_id>/', edit_client, name='edit_client'),
    path('list/', list_clients, name='list_clients'),
    path('individual-report/<int:pk>/', individual_report, name='individual_report'),
    path('generate-client-id/', generate_client_id_view, name='generate_client_id'),
    path('create-prospect/', create_prospect, name='create_prospect'),
    path('edit-prospect/<int:prospect_id>/', edit_prospect, name='edit_prospect'),
    path('prospects-list/', view_prospects, name='prospects_list'),
]
