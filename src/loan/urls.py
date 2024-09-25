from .views import  group_report, loan_upload_view, transaction_history, loan_payment, loan_registration, loan_detail, loan_schedule, loan_defaulters_report, loan_upload

from django.urls import path

urlpatterns = [
    path('transaction-history/<int:client_id>/', transaction_history, name='loan_transaction_history'),
    path('payment/', loan_payment, name='loan_payment'),
    path('registration/', loan_registration, name='loan_registration'),
    path('detail/<int:client_id>/', loan_detail, name='loan_detail'),
    path('schedule/<int:loan_id>/', loan_schedule, name='loan_schedule'),
    path('loan-defaulters-report/', loan_defaulters_report, name='loan_defaulters_report'),
    path('group-report/<int:pk>/', group_report, name='group_report'),
    path('upload/', loan_upload, name='loan_upload'),
    path('upload-loans/', loan_upload_view, name='loan_upload_bulk'),
    
]
