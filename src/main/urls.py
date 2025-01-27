from .views import group_detail, group_create, dashboard, update_app, get_accounts, journal_entry, fake_dashboard, group_edit, test_html
from .views import approve_journal_entry, disapprove_journal_entry, search, close_year_view

from django.urls import path

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('update/', update_app, name='update_app'),
    path('detail/<int:pk>/', group_detail, name='group_detail'),
    path('edit/<int:pk>/', group_edit, name='group_edit'),
    path('create_group/', group_create, name='group_create'),
    path('journal_entry/', journal_entry, name='journal_entry'),
    path('get-accounts/', get_accounts, name='get_accounts'),
    path('approve-journal-entry/<int:pk>/', approve_journal_entry, name='approve_journal_entry'),
    path('disapprove-journal-entry/<int:pk>/', disapprove_journal_entry, name='disapprove_journal_entry'),
    path('test-html/', test_html, name='test_html'),
    path('search/', search, name='search'),
    path('close-year/', close_year_view, name='close_year'),
]