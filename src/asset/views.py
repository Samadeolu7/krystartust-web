from django.shortcuts import render, redirect
from .forms import AssetForm

# Create your views here.

def create_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AssetForm()
    return render(request, 'asset_form.html', {'form': form})