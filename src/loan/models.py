from datetime import date
import datetime
from django.core.cache import cache
from django.db import models
from django.db.models import Case, When, BooleanField
from django.urls import reverse

from administration.models import TicketUpdates, Tickets
from client.models import Client
from user.models import User

class LoanManager(models.Manager):
    def with_is_defaulted(self):
        return self.annotate(
            is_defaulted=Case(
                When(repayment_schedule__due_date__lt=date.today(), repayment_schedule__is_paid=False, then=True),
                default=False,
                output_field=BooleanField()
            )
        )

class Loan(models.Model):
    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    LOAN_TYPE = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    loan_type = models.CharField(max_length=100, choices=LOAN_TYPE, db_index=True)
    duration = models.IntegerField()
    risk_premium = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    emi = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)
    created_by = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='loans', db_index=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = LoanManager()
    transaction = models.OneToOneField('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True, related_name='loans')
    approved = models.BooleanField(default=False)

    def is_approved(self):
        return self.approved

    @property
    def is_defaulted(self):
        cache_key = f"loan_{self.id}_is_defaulted"
        is_defaulted = cache.get(cache_key)
        if is_defaulted is None:
            repayment = self.repayment_schedule.filter(due_date__lt=date.today(), is_paid=False)
            is_defaulted = repayment.exists()
            if is_defaulted:
                repayment.first().handle_ticket()
            next_due_date = self.repayment_schedule.filter(is_paid=False).order_by('due_date').first()
            if next_due_date:
                next_due_date = next_due_date.due_date
                timeout = (next_due_date - date.today()).total_seconds()
                cache.set(cache_key, is_defaulted, timeout=timeout)
            else:
                cache.set(cache_key, is_defaulted)
        
        return is_defaulted

    def save(self, *args, **kwargs):
        # Invalidate the cache if the balance changes
        if self.pk is not None:
            orig = Loan.objects.get(pk=self.pk)
            if orig.balance != self.balance:
                cache_key = f"loan_{self.id}_is_defaulted"
                cache.delete(cache_key)
        # If loan is paid off, set status to closed
        if self.balance == 0:
            self.status = 'Closed'
        super().save(*args, **kwargs)
        
        # If the loan just closed, update the client's account status
        if self.status == 'Closed':
            self.client.update_account_status()

    def __str__(self) -> str:
        return f"{self.client.name} - {self.balance}"
    
    @classmethod
    def get_defaulted_loans(cls):
        defaulted_loans = []
        for loan in cls.objects.all():
            if loan.is_defaulted:
                defaulted_loans.append(loan)
        return defaulted_loans

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['client', 'loan_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]

class Guarantor(models.Model): 
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, db_index=True, related_name='guarantor')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_1 = models.TextField()
    address_2 = models.TextField()
    occupation = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

class LoanPayment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_index=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payment', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_schedule = models.ForeignKey('LoanRepaymentSchedule', on_delete=models.SET_NULL, db_index=True, null=True, blank=True)
    payment_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    transaction = models.OneToOneField('administration.Transaction', on_delete=models.CASCADE, null=True, blank=True, related_name='loan_payments')
    created_by = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='loan_payments', db_index=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            balance = self.loan.balance
            if balance != None:
                self.balance = balance - self.amount
                self.loan.balance = self.balance
                self.loan.save()
            else:
                self.balance = -self.amount
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        balance = self.loan.balance
        self.loan.balance = balance + self.amount
        self.payment_schedule.is_paid = False
        self.payment_schedule.payment_date = None
        self.payment_schedule.save()
        self.loan.save()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('loan_detail', kwargs={'id': self.loan.id})

    def __str__(self) -> str:
        return self.client.name + ' - ' + str(self.amount) + ' - ' + str(self.balance)
    
    class Meta:
        ordering = ['payment_date', 'created_at']
        indexes = [
            models.Index(fields=['client', 'loan']),
            models.Index(fields=['loan', 'payment_date']),
            models.Index(fields=['loan', 'payment_schedule']),
            models.Index(fields=['loan', 'created_at']),
        ]


class LoanRepaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayment_schedule', db_index=True)
    due_date = models.DateField(db_index=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False, db_index=True)
    payment_date = models.DateField(null=True, blank=True, db_index=True)

    def __str__(self) -> str:
        return self.loan.client.name + ' - ' + str(self.amount_due) + ' - ' + str(self.due_date)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.handle_ticket()
    
    def handle_ticket(self):
        ticket = Tickets.objects.filter(repayment_schedule=self, closed=False).first()
    
        if ticket:
            if self.is_paid:
                payment_date = self.payment_date
                if isinstance(payment_date, datetime.datetime):
                    payment_date = payment_date.date()
    
                if payment_date and payment_date <= self.due_date:
                    ticket.title = f"False Loan Default Alert for {self.loan.client.name}"
                    ticket.description += f"\nNo issue!!!\n Payment made on {self.payment_date} but uploaded on {self.payment_date}"
                    ticket.closed = True
                    ticket.save()
                elif payment_date and payment_date > self.due_date:
                    ticket.title = f"Loan Default Alert for {self.loan.client.name}"
                    ticket.description += f"\n Payment made on {self.payment_date} and uploaded on {self.payment_date}"
                    ticket.closed = True
                    ticket.save()
            else:
                if self.due_date > date.today():
                    update = TicketUpdates.objects.create(
                        ticket=ticket,
                        message=f"Due date for loan repayment schedule {self.id} has been updated to {self.due_date}",
                        created_by=User.objects.filter(is_superuser=True).first()
                    )
                    ticket.save()
                elif self.due_date < date.today():
                    ticket.title = f"Loan Default Alert for {self.loan.client.name}"
                    ticket.description += f"\nLoan defaulted. Loan Repayment Schedule ID: {self.id}"
                    ticket.save()
            return
    
        if not ticket and self.due_date < date.today() and not self.is_paid:
            new_ticket = Tickets.objects.create(
                client=self.loan.client,
                title=f"Loan Default Alert for {self.loan.client.name}",
                description=f"Loan defaulted. Loan Repayment Schedule ID: {self.id}",
                priority='n',
                closed=False,
                created_by=User.objects.filter(is_superuser=True).first(),
                repayment_schedule=self
            )
            new_ticket.users.set(User.objects.all())
            new_ticket.save()
    class Meta:
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['loan', 'due_date']),
            models.Index(fields=['loan', 'is_paid']),
            models.Index(fields=['loan', 'due_date', 'is_paid']),
            models.Index(fields=['loan', 'due_date', 'payment_date']),
        ]