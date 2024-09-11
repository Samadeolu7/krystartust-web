from .views import all_clients_report, all_groups_report, daily_transactions_report

from django.urls import path

urlpatterns = [
    
    path('all-clients-report/', all_clients_report, name='all_clients_report'),
    path('all-groups-report/', all_groups_report, name='all_groups_report'),
    path('daily-transactions-report/', daily_transactions_report, name='daily_transactions_report'),

]
