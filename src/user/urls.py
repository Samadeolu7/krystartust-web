from django.urls import path

from .views import add_user, user_list, user_detail, user_update

urlpatterns = [
    path('add/', add_user, name='create_users'),
    path('list/', user_list, name='list_users'),
    path('detail/<int:user_id>/', user_detail, name='user_detail'),
    path('update/<int:user_id>/', user_update, name='user_update'),
]