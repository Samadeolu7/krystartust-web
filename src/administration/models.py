from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from user.models import User

# Create your models here.

class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    transportation = models.DecimalField(max_digits=10, decimal_places=2)
    food = models.DecimalField(max_digits=10, decimal_places=2)
    house_rent = models.DecimalField(max_digits=10, decimal_places=2)
    utility = models.DecimalField(max_digits=10, decimal_places=2)
    entertainment = models.DecimalField(max_digits=10, decimal_places=2)
    leave = models.DecimalField(max_digits=10, decimal_places=2)    

    def __str__(self):
        return self.user.name


class Approval(models.Model):
    TYPES = (
        ('Expenses', 'Expenses'),
        ('Loan', 'Loan'),
    )
    type = models.CharField(max_length=100, choices=TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.rejected:
            
            super().save(*args, **kwargs)
            # Delete the related object
            self.content_object.delete()
        else:
            # Set the approved attribute on the related object to True
            self.content_object.approved = True
            self.content_object.save()
            super().save(*args, **kwargs)