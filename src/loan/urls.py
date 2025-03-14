from .views import  extend_loan, group_report, load_payment_schedules, loan_upload_view
from .views import transaction_history, loan_payment, loan_registration, loan_detail, loan_schedule
from .views import loan_defaulters_report, loan_upload, load_payment_schedules_com, guarantor_for_loan
from .views import load_loans, load_savings_balance, loan_payment_from_savings_view

from django.urls import path

urlpatterns = [
    path('transaction-history/<int:client_id>/', transaction_history, name='loan_transaction_history'),
    path('payment/', loan_payment, name='loan_payment'),
    path('registration/', loan_registration, name='loan_registration'),
    path('detail/<int:id>/', loan_detail, name='loan_detail'),
    path('schedule/<int:loan_id>/', loan_schedule, name='loan_schedule'),
    path('loan-defaulters-report/', loan_defaulters_report, name='loan_defaulters_report'),
    path('group-report/<int:pk>/', group_report, name='group_report'),
    path('upload/', loan_upload, name='loan_upload'),
    path('upload-loans/', loan_upload_view, name='loan_upload_bulk'),
    path('ajax/load-payment-schedules/', load_payment_schedules, name='load_payment_schedules'),
    path('ajax/load-payment-schedules-com/', load_payment_schedules_com, name='load_payment_schedules_com'),
    path('guarantor-for-loan/<int:loan_id>/', guarantor_for_loan, name='guarantor_for_loan'),
    path('load-loans/', load_loans, name='load_loans'),
    path('load-savings-balance/', load_savings_balance, name='load_savings_balance'),
    path('loan-payment-from-savings/', loan_payment_from_savings_view, name='loan_payment_from_savings'),

    path('extend-loan/', extend_loan, name='extend_loan'),
]
