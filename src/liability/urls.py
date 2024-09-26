from django.urls import path

from .views import create_liability, liability_payment, liability_list, liability_detail


urlpatterns = [
    path('create', create_liability, name='create_liability'),
    path('payment/', liability_payment, name='liability_payment'),
    path('list/', liability_list, name='liability_list'),
    path('detail/<int:pk>/', liability_detail, name='liability_detail'),
]
