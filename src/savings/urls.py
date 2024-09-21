from .views import transaction_history, register_savings, record_withdrawal, compulsory_savings, upload_savings
from django.urls import path

urlpatterns = [
    path('compulsory-savings/', compulsory_savings, name='compulsory_savings'),
    path('transaction-history/<int:client_id>/', transaction_history, name='transaction_history'),
    path('register/', register_savings, name='savings_registration'),
    path('withdraw/', record_withdrawal, name='savings_withdrawal'),
    path('upload/', upload_savings, name='savings_upload'),
]