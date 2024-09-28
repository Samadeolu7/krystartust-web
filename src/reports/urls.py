from .views import all_clients_report, all_groups_report, client_loans_payments_excel, client_savings_payments_excel, daily_transactions_report, defaulter_report_excel, individual_group_report, profit_and_loss_report, trial_balance_report, client_list_excel

from django.urls import path

urlpatterns = [
    path('all-clients-report/', all_clients_report, name='all_clients_report'),
    path('all-groups-report/', all_groups_report, name='all_groups_report'),
    path('individual-group-report/<int:group_id>/', individual_group_report, name='individual_group_report'),
    path('daily-transactions-report/', daily_transactions_report, name='daily_transactions_report'),
    path('pandl-report/', profit_and_loss_report, name='profit_and_loss_report'),
    path('trial-balance-report/', trial_balance_report, name='trial_balance'),
    path('client-list-excel/', client_list_excel, name='client_list_excel'),
    path('defaulter-report-excel/', defaulter_report_excel, name='defaulter_report_excel'),
    path('client-savings-payments-excel/<int:client_id>/', client_savings_payments_excel, name='client_savings_payments_excel'),
    path('client-loans-payments-excel/<int:client_id>/', client_loans_payments_excel, name='client_loans_payments_excel'),
    
]
