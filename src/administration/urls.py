from django.urls import path

from .views import salary, approvals, approve, disapprove, approval_history, approval_detail, download_payslip, ticket_reassign
from .views import manage_month_status, ticket_create, ticket_detail, ticket_list, ticket_close, ticket_update

urlpatterns = [
    path('salary/', salary, name='salary'),
    path('approvals/', approvals, name='approvals'),
    path('approve/<int:pk>/', approve, name='approve'),
    path('disapprove/<int:pk>/', disapprove, name='disapprove'),
    path('approval-history/', approval_history, name='approval_history'),
    path('approval-detail/<int:pk>/', approval_detail, name='approval_detail'),
    path('download-payslip/<int:notification_id>/', download_payslip, name='download_payslip'),
    path('manage-month-status/', manage_month_status, name='manage_month_status'),
    path('ticket-create/', ticket_create, name='ticket_create'),
    path('ticket-list/', ticket_list, name='ticket_list'),
    path('ticket-list/<int:client_id>/', ticket_list, name='ticket_list'),
    path('ticket-detail/<int:pk>/', ticket_detail, name='ticket_detail'),
    path('ticket-close/<int:pk>/', ticket_close, name='ticket_close'),
    path('ticket-update/<int:pk>/', ticket_update, name='ticket_update'),
    path('tickets/<int:pk>/reassign/', ticket_reassign, name='ticket_reassign'),
    
]