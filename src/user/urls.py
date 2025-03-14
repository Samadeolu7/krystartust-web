from django.urls import path

from .views import add_user, record_salary_expense_view, user_list, user_detail, user_update, change_password

urlpatterns = [
    path('add/', add_user, name='create_users'),
    path('list/', user_list, name='user_list'),
    path('detail/<int:user_id>/', user_detail, name='user_detail'),
    path('update/<int:user_id>/', user_update, name='user_update'),
    path('delete/<int:user_id>/', user_update, name='user_delete'),
    path('change_password/<int:user_id>/', change_password, name='change_password'),
    path('record-salary-expense/', record_salary_expense_view, name='record_salary_expense'),

]