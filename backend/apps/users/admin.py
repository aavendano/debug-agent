"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_store_owner', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_store_owner', 'is_active', 'is_verified', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'business_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone', 'avatar', 'bio')
        }),
        (_('Address'), {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        (_('Business info'), {
            'fields': ('is_store_owner', 'business_name', 'tax_id')
        }),
        (_('Social media'), {
            'fields': ('social_media',)
        }),
        (_('Preferences'), {
            'fields': ('language', 'timezone')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
    
    ordering = ('-created_at',)
