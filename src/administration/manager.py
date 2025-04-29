from django.db import models
from django.core.exceptions import PermissionDenied

class OfficeScopedManager(models.Manager):
    def for_user(self, user):
        if not user.is_authenticated:
            raise PermissionDenied("User must be authenticated to access office-scoped data.")
        if not user.office:
            raise PermissionDenied("User must be assigned to an office to access data.")
        return self.filter(office=user.office)