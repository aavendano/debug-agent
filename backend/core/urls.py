"""
URL configuration for ecommerce platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/', include([
        path('auth/', include('rest_framework_simplejwt.urls')),
        path('stores/', include('apps.stores.urls')),
        path('users/', include('apps.users.urls')),
        path('products/', include('apps.products.urls')),
        path('categories/', include('apps.categories.urls')),
        path('orders/', include('apps.orders.urls')),
        path('seo/', include('apps.seo.urls')),
        path('analytics/', include('apps.analytics.urls')),
    ])),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
