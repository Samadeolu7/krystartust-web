from .views import all_clients_report, all_groups_report, client_loans_payments_excel, balance_sheet_report
from .views import client_savings_payments_excel, daily_transactions_report, defaulter_report_excel
from .views import individual_group_report, profit_and_loss_report, trial_balance_report, client_list_excel
from .views import weekly_cash_flow_report, report_summary_by_date, daily_report, thrift_report, individual_thrift_report

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('all-clients-report/', all_clients_report, name='all_clients_report'),
    path('all-groups-report/', all_groups_report, name='all_groups_report'),
    path('individual-group-report/<int:group_id>/', individual_group_report, name='individual_group_report'),
    path('daily-transactions-report/', daily_transactions_report, name='daily_transactions_report'),
    path('pandl-report/', profit_and_loss_report, name='profit_and_loss_report'),
    path('trial-balance-report/', trial_balance_report, name='trial_balance'),
    path('balance-sheet-report/', balance_sheet_report, name='balance_sheet_report'),
    path('client-list-excel/', client_list_excel, name='client_list_excel'),
    path('defaulter-report-excel/', defaulter_report_excel, name='defaulter_report_excel'),
    path('client-savings-payments-excel/<int:client_id>/', client_savings_payments_excel, name='client_savings_payments_excel'),
    path('client-loans-payments-excel/<int:client_id>/', client_loans_payments_excel, name='client_loans_payments_excel'),
    path('weekly-cash-flow-report/', weekly_cash_flow_report, name='weekly_cash_flow_report'),
    path('report-summary-by-date/', report_summary_by_date, name='report_summary_by_date'),
    path('daily-report/', daily_report, name='daily_report'),
    path('thrift-report/', thrift_report, name='thrift_report'),
    path('individual-thrift-report/<int:id>/', individual_thrift_report, name='individual_thrift_report'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)