from .views import registration_fee, id_fee, loan_registration_fee, risk_premium, union_contribution, loan_service_fee, set_fees
from django.urls import path

urlpatterns = [
    path('set_fee/', set_fees, name='set_fees'),
    path('registration_fee/', registration_fee, name='registration_fee'),
    path('id_fee/', id_fee, name='id_fee'),
    path('loan_registration_fee/', loan_registration_fee, name='loan_registration_fee'),
    path('risk_premium/', risk_premium, name='risk_premium'),
    path('union_contribution/', union_contribution, name='union_contribution'),
    path('loan_service_fee/', loan_service_fee, name='loan_service_fee'),
]