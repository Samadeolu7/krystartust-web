from .views import register_savings, record_withdrawal, compulsory_savings, setup_monthly_contributions_view, toggle_daily_contribution_view, upload_savings, savings_detail, register_payment, record_client_contribution
from .views import daily_contribution_report, multi_day_contribution_view, fetch_contributions
from .views import daily_contribution_spreadsheet, daily_contribution_spreadsheet_form

from django.urls import path

urlpatterns = [
    path('compulsory-savings/', compulsory_savings, name='compulsory_savings'),
    path('savings_detail/<int:client_id>/', savings_detail, name='savings_detail'),
    path('register/', register_savings, name='savings_registration'),
    path('withdraw/', record_withdrawal, name='savings_withdrawal'),
    path('upload/', upload_savings, name='savings_upload'),
    path('payment/', register_payment, name='register_payment'),
    path('setup-monthly-contributions/', setup_monthly_contributions_view, name='setup_monthly_contributions'),
    path('toggle-daily-contribution/', toggle_daily_contribution_view, name='toggle_daily_contribution'),
    path('record-client-contribution/', record_client_contribution, name='record_client_contribution'),
    path('daily-contribution-report/', daily_contribution_report, name='daily_contribution_report'),
    path('daily-contribution-spreadsheet/', daily_contribution_spreadsheet, name='daily_contribution_spreadsheet'),
    path('daily-contribution-spreadsheet-form/', daily_contribution_spreadsheet_form, name='daily_contribution_spreadsheet_form'),
    path('multi-day-contribution/', multi_day_contribution_view, name='multi_day_contribution'),
    path('fetch-contributions/<int:client_contribution_id>/', fetch_contributions, name='fetch_contributions'),
]