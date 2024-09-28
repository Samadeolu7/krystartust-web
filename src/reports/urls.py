from .views import all_clients_report, all_groups_report, daily_transactions_report, profit_and_loss_report, trial_balance_report, client_list_excel

from django.urls import path

urlpatterns = [
    path('all-clients-report/', all_clients_report, name='all_clients_report'),
    path('all-groups-report/', all_groups_report, name='all_groups_report'),
    path('daily-transactions-report/', daily_transactions_report, name='daily_transactions_report'),
    path('pandl-report/', profit_and_loss_report, name='profit_and_loss_report'),
    path('trial-balance-report/', trial_balance_report, name='trial_balance'),
    path('client-list-excel/', client_list_excel, name='client_list_excel'),
]
