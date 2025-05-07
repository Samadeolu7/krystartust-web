import calendar
from datetime import datetime
import os

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Case, When, Value, IntegerField

from administration.decorators import allowed_users
from expenses.utils import approve_expense
from main.models import JournalEntry, Year
from main.utils import verify_trial_balance
from user.pdf_gen import generate_payslip
from .models import Approval, MonthStatus, Notification, Tickets
from loan.utils import approve_loan, disapprove_loan
from .forms import SalaryForm, TicketForm, TicketReassignForm, TicketUpdateForm

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
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    if not is_admin:
        loan = Approval.Loan
        cash_transfer = Approval.Cash_Transfer
        approvals = Approval.objects.filter(approved=False,type=cash_transfer,rejected=False)
        return render(request, 'approvals.html', {'approvals': approvals})
    approvals = Approval.objects.filter(approved=False, rejected=False)
    journals = JournalEntry.objects.filter(approved=False, rejected=False)
    return render(request, 'approvals.html', {'approvals': approvals, 'journals': journals})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def approve(request, pk):
    approval = Approval.objects.get(pk=pk)
    with transaction.atomic():
        approval = Approval.objects.select_for_update().get(pk=pk)
        if approval.type == Approval.Loan:
            approve_loan(approval, request.user)
        elif approval.type == Approval.Expenses:
            approve_expense(approval, request.user)
        elif approval.type == Approval.Batch_Expense:
            batch = approval.content_object
            batch.approve(request.user)
        elif approval.type == Approval.Salary:
            approve_expense(approval, request.user)
            generate_payslip(approval.user)
        elif approval.type == Approval.Cash_Transfer:
            approval.approved = True
            approval.approved_by = request.user
            approval.save()
            verify_trial_balance()
            return redirect('approvals')
        approval.approved = True
        approval.approved_by = request.user
        approval.save()
        verify_trial_balance()
    return redirect('approvals')

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def disapprove(request, pk):
    approval = Approval.objects.get(pk=pk)
    if approval.type == Approval.Loan:
        disapprove_loan(approval, request.user)
        return redirect('approvals')
    approval.rejected = True
    approval.approved_by = request.user
    approval.save()
    return redirect('approvals')

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def approval_detail(request, pk):
    approval = Approval.objects.get(pk=pk)
    context = {
        'approval': approval,
    }
    if approval.type == Approval.Loan:
        context['loan'] = approval.content_object
        context['guarantor'] = approval.content_object.guarantor
    elif approval.type == Approval.Withdrawal:
        context['withdrawal'] = approval.content_object
    elif approval.type == Approval.Salary:
        context['salary'] = approval.content_object
    elif approval.type == Approval.Expenses:
        context['expense'] = approval.content_object
    elif approval.type == Approval.Batch_Expense:
        context['batch'] = approval.content_object
    elif approval.type == Approval.Cash_Transfer:
        context['transfer'] = approval.content_object

    return render(request, 'approval_detail.html', context)


@login_required
@allowed_users(allowed_roles=['Admin'])
def approval_history(request):
    approvals = Approval.objects.filter(approved=True, rejected=True)
    return render(request, 'approval_history.html', {'approvals': approvals})


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


@login_required
@allowed_users(allowed_roles=['Admin'])
def manage_month_status(request):
    current_year = Year.current_year()

    # Generate month statuses for the current year if they don't exist
    for month in range(1, 13):
        MonthStatus.objects.get_or_create(month=month, year=current_year)

    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        month_status = MonthStatus.objects.get(month=month, year=year)
        month_status.is_closed = not month_status.is_closed
        month_status.save()
        return redirect('manage_month_status')

    month_statuses = MonthStatus.objects.filter(year=current_year).order_by('month')
    for month_status in month_statuses:
        month_status.month_name = calendar.month_name[month_status.month]
   
    return render(request, 'manage_month_status.html', {'month_statuses': month_statuses, 'current_year': current_year})


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def ticket_list(request, client_id=None):
    priority_order = Case(
        When(priority='e', then=Value(1)),
        When(priority='h', then=Value(2)),
        When(priority='n', then=Value(3)),
        When(priority='l', then=Value(4)),
        output_field=IntegerField(),
    )
    
    if client_id:
        tickets = Tickets.objects.filter(client=client_id).order_by(priority_order, '-created_at')
    else:
        tickets = Tickets.objects.filter(closed=False).order_by(priority_order, '-created_at')
    
    return render(request, 'ticket_list.html', {'tickets': tickets})
from .forms import TicketUpdateForm, TicketReassignForm

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def ticket_detail(request, pk):
    ticket = get_object_or_404(Tickets, pk=pk)
    ticket_updates = ticket.updates.all()
    
    update_form = TicketUpdateForm()
    reassign_form = TicketReassignForm()

    context = {
        'ticket': ticket,
        'ticket_updates': ticket_updates,
        'update_form': update_form,
        'reassign_form': reassign_form,
    }
    return render(request, 'ticket_detail.html', context=context)


@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def ticket_create(request, client_id=None):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.instance.created_by = request.user
            form.save()

            return redirect('dashboard')
    else:
        form = TicketForm()
        #add client to form
        if client_id:
            form.fields['client'].initial = client_id
    return render(request, 'ticket_form.html', {'form': form})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def ticket_update(request, pk):
    ticket = get_object_or_404(Tickets, pk=pk)
    if request.method == "POST":
        form = TicketUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.ticket = ticket
            update.created_by = request.user
            update.save()
            return redirect('ticket_detail', pk=pk)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, 'ticket_detail.html', {'form': form, 'ticket': ticket})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def ticket_reassign(request, pk):
    ticket = get_object_or_404(Tickets, pk=pk)
    if request.method == "POST":
        form = TicketReassignForm(request.POST, instance=ticket)
        if form.is_valid():
            new_user = form.cleaned_data['new_user']
            ticket.users.set([new_user])
            ticket.save()
            return redirect('ticket_detail', pk=pk)
    else:
        form = TicketReassignForm(instance=ticket)
    return render(request, 'ticket_reassign.html', {'form': form, 'ticket': ticket})

@login_required
@allowed_users(allowed_roles=['Admin', 'Manager'])
def ticket_close(request, pk):
    ticket = get_object_or_404(Tickets, pk=pk)
    ticket.close(request.user)
    return redirect('ticket_detail', pk=pk)