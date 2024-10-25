import os
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from administration.decorators import allowed_users
from expenses.utils import approve_expense
from user.pdf_gen import generate_payslip
from .models import Approval, Notification
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

    if approval.type == Approval.Loan:
        approve_loan(approval, request.user)
        return redirect('approvals')
    elif approval.type == Approval.Expenses:
        print("Approving expense")
        approve_expense(approval, request.user)

        return redirect('approvals')
    elif approval.type == Approval.Salary:
        print("Approving salary")
        approve_expense(approval, request.user)
        print("Generating payslip")
        generate_payslip(approval.user)
        print("Payslip generated")
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

@login_required
def download_payslip(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    payslip_path = notification.payslip_url
    
    if os.path.exists(payslip_path):
        with open(payslip_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(payslip_path)}"'
           
        # Mark notification as read and delete the payslip
        notification.is_read = True
        notification.save()
        os.remove(payslip_path)
        
        return response
    else:
        raise Http404("Payslip not found")