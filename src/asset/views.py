from django.shortcuts import render, redirect
from .forms import AssetForm
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def create_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AssetForm()
    return render(request, 'asset_form.html', {'form': form})