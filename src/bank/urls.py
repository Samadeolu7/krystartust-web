from .views import create_bank, create_bank_payment, bank_list, bank_detail

from django.urls import path

urlpatterns = [
    path('create/', create_bank, name='create_bank'),
    path('create-payment/', create_bank_payment, name='create_bank_payment'),
    path('list/', bank_list, name='bank_list'),
    path('detail/<int:pk>/', bank_detail, name='bank_detail'),
]