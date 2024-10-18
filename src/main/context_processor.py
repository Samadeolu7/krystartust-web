from django.contrib.auth.models import Group

def user_groups(request):
    if request.user.is_authenticated:
        user_groups = Group.objects.filter(user=request.user)
        if user_groups.exists():
            if user_groups.first().name == 'Admin':
                return {'is_admin': True}
            elif user_groups.first().name == 'Manager':
                return {'is_manager': True}
            elif user_groups.first().name == 'staff':
                return {'is_staff': True}
            else:
                return {'is_client': True}
        else:
            return {'is_client': True}
    else:
        return {}