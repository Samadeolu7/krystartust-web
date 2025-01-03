from .views import create_bank, create_bank_payment, bank_list, bank_detail, cash_transfer,bank_to_excel_view
from .views import update_payments, payment_reversal as reverse_payment

from django.urls import path

urlpatterns = [
    path('create/', create_bank, name='create_bank'),
    path('create-payment/', create_bank_payment, name='create_bank_payment'),
    path('list/', bank_list, name='bank_list'),
    path('detail/<int:pk>/', bank_detail, name='bank_detail'),
    path('update/<int:pk>/', create_bank, name='update_bank'),
    path('transfer/', cash_transfer, name='cash_transfer'),
    path('excel/<int:pk>/', bank_to_excel_view, name='bank_to_excel'),
    path('update-payments/', update_payments, name='update_payments'),
    path('reverse-payment/', reverse_payment, name='reverse_payment'),
]
