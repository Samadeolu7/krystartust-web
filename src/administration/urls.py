from django.urls import path

from .views import salary, approvals, approve, disapprove, approval_history, approval_detail, download_payslip
from .views import manage_month_status

urlpatterns = [
    path('salary/', salary, name='salary'),
    path('approvals/', approvals, name='approvals'),
    path('approve/<int:pk>/', approve, name='approve'),
    path('disapprove/<int:pk>/', disapprove, name='disapprove'),
    path('approval-history/', approval_history, name='approval_history'),
    path('approval-detail/<int:pk>/', approval_detail, name='approval_detail'),
    path('download-payslip/<int:notification_id>/', download_payslip, name='download_payslip'),
    path('manage-month-status/', manage_month_status, name='manage_month_status'),
]