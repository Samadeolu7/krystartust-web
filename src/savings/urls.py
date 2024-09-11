from .views import transaction_history, register_savings, record_withdrawal

from django.urls import path

urlpatterns = [
    path('transaction-history/<int:client_id>/', transaction_history, name='transaction_history'),
    path('register/', register_savings, name='savings_registration'),
    path('withdraw/', record_withdrawal, name='savings_withdrawal'),
]