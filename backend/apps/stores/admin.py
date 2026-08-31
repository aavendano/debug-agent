"""
Admin configuration for stores app.
"""
from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Store, Domain


@admin.register(Store)
class StoreAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', 'ai_provider', 'ai_model', 'is_active', 'created_at')
    list_filter = ('is_active', 'ai_provider', 'created_at')
    search_fields = ('name', 'slug', 'owner__email', 'ai_api_key')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'owner', 'description', 'theme', 'is_active', 'is_public')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon')
        }),
        ('SEO Defaults', {
            'fields': ('seo_default_keywords', 'default_meta_title', 'default_meta_description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'social_media')
        }),
        ('AI Configuration', {
            'fields': (
                'ai_provider', 'ai_api_key', 'ai_base_url', 'ai_model',
                'ai_max_tokens', 'ai_temperature', 'ai_auto_generate_seo',
                'ai_budget_monthly', 'ai_tokens_used_monthly', 'ai_cost_used_monthly'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        # For superusers, show all stores
        if request.user.is_superuser:
            return Store.objects.all()
        # For regular users, show only their stores
        return Store.objects.filter(owner=request.user)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
