from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _

class UserAdmin(DefaultUserAdmin):
    model = User
    list_display = ('email', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    ordering = ('email',)
    search_fields = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),  # Ensure these fields exist in your User model
        (_('Personal info'), {'fields': ('salary',)}),  # Ensure 'salary' exists in your User model
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),  # Ensure 'last_login' exists in your User model
    )

admin.site.register(User, UserAdmin)