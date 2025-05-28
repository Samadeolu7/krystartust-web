from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

from main.utils import verify_trial_balance
from .models import AssetCategory, FixedAsset, Inventory, AssetRecord
from .forms import AssetCategoryForm, FixedAssetForm, InventoryForm, AssetRecordForm
from .utils import depreciate_fixed_assets


@login_required
def asset_category_list(request):
    categories = AssetCategory.objects.all()
    return render(request, 'asset_category_list.html', {'categories': categories})


@login_required
def asset_category_create(request):
    if request.method == 'POST':
        form = AssetCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_category_list')
    else:
        form = AssetCategoryForm()
    return render(request, 'asset_category_form.html', {'form': form})


@login_required
def fixed_asset_list(request):
    assets = FixedAsset.objects.all()
    return render(request, 'fixed_asset_list.html', {'assets': assets})


@login_required
def fixed_asset_create(request):
    if request.method == 'POST':
        form = FixedAssetForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save(user=request.user)
                verify_trial_balance()
                return redirect('fixed_asset_list')
    else:
        form = FixedAssetForm()
    return render(request, 'fixed_asset_form.html', {'form': form})


@login_required
def inventory_list(request):
    items = Inventory.objects.all()
    return render(request, 'inventory_list.html', {'items': items})


@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                verify_trial_balance()
                return redirect('inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'inventory_form.html', {'form': form})


@login_required
def asset_record_list(request):
    records = AssetRecord.objects.all()
    return render(request, 'asset_record_list.html', {'records': records})


@login_required
def asset_record_create(request):
    if request.method == 'POST':
    
        form = AssetRecordForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                verify_trial_balance()
                return redirect('asset_record_list')
    else:
        form = AssetRecordForm()
    return render(request, 'asset_record_form.html', {'form': form})