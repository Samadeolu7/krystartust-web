from django.urls import path

from .views import create_expense, expense_payment, expense_list, expense_detail, create_expense_type, create_expense_payment_batch


urlpatterns = [
    path('create', create_expense, name='create_expense'),
    path('create_type/', create_expense_type, name='create_expense_type'),
    path('payment/', expense_payment, name='expense_payment'),
    path('list/', expense_list, name='expense_list'),
    path('detail/<int:pk>/', expense_detail, name='expense_detail'),
    path('create_batch/', create_expense_payment_batch, name='create_expense_payment_batch'),
]
