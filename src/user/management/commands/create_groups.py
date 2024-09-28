# management/commands/create_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create default groups and permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        manager_group, created = Group.objects.get_or_create(name='Manager')
        staff_group, created = Group.objects.get_or_create(name='Staff')

        # Assign permissions to groups
        # Example: Add 'add_user' permission to Admin group
        add_user_permission = Permission.objects.get(codename='add_user')
        admin_group.permissions.add(add_user_permission)

        # Add other permissions as needed

        self.stdout.write(self.style.SUCCESS('Successfully created groups and assigned permissions'))