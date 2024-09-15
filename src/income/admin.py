from django.contrib import admin
from .models import Income, IncomePayment, IDFee, RegistrationFee, RiskPremium, UnionContribution, LoanRegistrationFee, LoanServiceFee

# Register your models here.

admin.site.register(Income)
admin.site.register(IncomePayment)
admin.site.register(IDFee)
admin.site.register(RegistrationFee)
admin.site.register(RiskPremium)
admin.site.register(UnionContribution)
admin.site.register(LoanRegistrationFee)
admin.site.register(LoanServiceFee)