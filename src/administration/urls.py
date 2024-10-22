from django.urls import path

from .views import salary, approvals, approve, disapprove, approval_history, approval_detail

urlpatterns = [
    path('salary/', salary, name='salary'),
    path('approvals/', approvals, name='approvals'),
    path('approve/<int:pk>/', approve, name='approve'),
    path('disapprove/<int:pk>/', disapprove, name='disapprove'),
    path('approval-history/', approval_history, name='approval_history'),
    path('approval-detail/<int:pk>/', approval_detail, name='approval_detail'),
]