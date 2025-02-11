from django.db import OperationalError, models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from client.models import Client
from user.models import User    

# Create your models here.
class ClientGroup(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='client_groups')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Year(models.Model):
    year = models.IntegerField()

    def __str__(self):
        return str(self.year)
    
    @classmethod
    def current_year(cls):
        try:
            last_year_instance = cls.objects.order_by('-year').first()
            if last_year_instance:
                return last_year_instance.year
            else:
                return 2024
        except (cls.DoesNotExist, OperationalError):
            return 2024
        
        
    class Meta:
        ordering = ['-year']
        

class JournalEntry(models.Model):
    credit_account = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='credit_entries')
    credit_id = models.PositiveIntegerField()
    credit_object = GenericForeignKey('credit_account', 'credit_id')
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    debit_account = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='debit_entries')
    debit_id = models.PositiveIntegerField()
    debit_object = GenericForeignKey('debit_account', 'debit_id')
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField()
    payment_date = models.DateField()
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')


class YearEndEntry(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='year_end_entries')
    total_savings = models.DecimalField(max_digits=10, decimal_places=2)
    total_loans = models.DecimalField(max_digits=10, decimal_places=2)
    retained_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-year']