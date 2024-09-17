from .views import group_view, group_detail, group_create, dashboard, update_app

from django.urls import path

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('update/', update_app, name='update_app'),
    path('detail/<int:pk>/', group_detail, name='group_detail'),
    path('create_group/', group_create, name='group_create'),
    path('view_groups/', group_view, name='group_view'),
]