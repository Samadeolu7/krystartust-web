from .views import group_view, group_detail, group_create, dashboard, update_app, get_accounts, journal_entry, fake_dashboard

from django.urls import path

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('update/', update_app, name='update_app'),
    path('detail/<int:pk>/', group_detail, name='group_detail'),
    path('create_group/', group_create, name='group_create'),
    path('view_groups/', group_view, name='group_view'),
    path('journal_entry/', journal_entry, name='journal_entry'),
    path('get-accounts/', get_accounts, name='get_accounts'),
    path('2/', fake_dashboard, name='fake_dashboard'),
]