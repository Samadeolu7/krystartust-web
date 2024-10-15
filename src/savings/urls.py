from .views import register_savings, record_withdrawal, compulsory_savings, upload_savings, savings_detail, register_payment
from django.urls import path

urlpatterns = [
    path('compulsory-savings/', compulsory_savings, name='compulsory_savings'),
    path('savings_detail/<int:client_id>/', savings_detail, name='savings_detail'),
    path('register/', register_savings, name='savings_registration'),
    path('withdraw/', record_withdrawal, name='savings_withdrawal'),
    path('upload/', upload_savings, name='savings_upload'),
    path('payment/', register_payment, name='register_payment'),
]