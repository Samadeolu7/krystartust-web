from django.contrib import admin
from .models import Loan, LoanPayment, LoanRepaymentSchedule, Guarantor

class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ('client', 'loan', 'amount', 'balance', 'payment_date', 'created_at')
    search_fields = ('client__name', 'loan__id')
    list_filter = ('payment_date', 'created_at')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('client', 'loan', 'payment_schedule', 'transaction', 'created_by')
        queryset = queryset.prefetch_related('loan__repayment_schedule')
        return queryset

class LoanAdmin(admin.ModelAdmin):
    list_display = ('client', 'amount', 'balance', 'loan_type', 'start_date', 'end_date', 'status')
    search_fields = ('client__name', 'id')
    list_filter = ('loan_type', 'start_date', 'end_date', 'status')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('client', 'created_by', 'transaction')
        queryset = queryset.prefetch_related('repayment_schedule')
        return queryset

class LoanRepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('loan', 'due_date', 'amount_due', 'is_paid', 'payment_date')
    search_fields = ('loan__client__name', 'loan__id')
    list_filter = ('due_date', 'is_paid', 'payment_date')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('loan', 'loan__client')
        return queryset

admin.site.register(Loan, LoanAdmin)
admin.site.register(LoanPayment, LoanPaymentAdmin)
admin.site.register(LoanRepaymentSchedule, LoanRepaymentScheduleAdmin)
admin.site.register(Guarantor)