from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import SalaryForm

# Create your views here.

@login_required
def salary(request):
    form = SalaryForm()
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    return render(request, 'administration/salary.html', {'form': form})

