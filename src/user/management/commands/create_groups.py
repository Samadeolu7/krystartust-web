from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from user.models import User as CustomUser

class Command(BaseCommand):
    help = 'Create groups for the application and assign permissions'

    def handle(self, *args, **kwargs):
        # Create the groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        staff_group, _ = Group.objects.get_or_create(name='Staff')

        # Get the content types
        user_content_type = ContentType.objects.get_for_model(CustomUser)

        # Define permissions
        permissions = {
            'Admin': ['add_user', 'change_user', 'delete_user', 'view_user'],
            'Manager': ['add_user', 'change_user', 'view_user'],
            'Staff': ['view_user'],
        }

        # Assign permissions to groups
        for group_name, perm_codes in permissions.items():
            group = Group.objects.get(name=group_name)
            for perm_code in perm_codes:
                permission = Permission.objects.get(codename=perm_code, content_type=user_content_type)
                group.permissions.add(permission)

        # Ensure superusers are in the Admin group and have all permissions
        superusers = CustomUser.objects.filter(is_superuser=True)
        for superuser in superusers:
            superuser.groups.add(admin_group)
            superuser.user_permissions.set(Permission.objects.all())

        self.stdout.write(self.style.SUCCESS('Successfully created groups, assigned permissions, and ensured superusers have all permissions'))