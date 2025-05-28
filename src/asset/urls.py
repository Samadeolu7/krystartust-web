from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.asset_category_list, name='asset_category_list'),
    path('categories/create/', views.asset_category_create, name='asset_category_create'),
    path('fixed-assets/', views.fixed_asset_list, name='fixed_asset_list'),
    path('fixed-assets/create/', views.fixed_asset_create, name='fixed_asset_create'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
    path('records/', views.asset_record_list, name='asset_record_list'),
    path('records/create/', views.asset_record_create, name='asset_record_create'),
]