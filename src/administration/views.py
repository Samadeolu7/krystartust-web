from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from administration.decorators import allowed_users
from .models import Approval
from loan.utils import approve_loan
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


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def approvals(request):
    #check if user is admin
    if request.user.is_staff:
        approvals = Approval.objects.filter(approved=False,type='loan')
    approvals = Approval.objects.filter(approved=False)
    
    return render(request, 'approvals.html', {'approvals': approvals})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def approve(request, pk):
    approval = Approval.objects.get(pk=pk)
    print(approval.type)
    if approval.type == 'Loan':
        print('Approving loan')
        approve_loan(approval, request.user)
        return redirect('approvals')
    approval.approved = True
    approval.approved_by = request.user
    approval.save()
    return redirect('approvals')

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def disapprove(request, pk):
    approval = Approval.objects.get(pk=pk)
    approval.rejected = True
    approval.approved_by = request.user
    approval.save()
    return redirect('approvals')

@login_required
@allowed_users(allowed_roles=['Admin'])
def approval_history(request):
    approvals = Approval.objects.filter(approved=True, rejected=True)
    return render(request, 'approval_history.html', {'approvals': approvals})

@login_required
@allowed_users(allowed_roles=['Admin'])
def approval_detail(request, pk):
    approval = Approval.objects.get(pk=pk)
    return render(request, 'approval_detail.html', {'approval': approval})
