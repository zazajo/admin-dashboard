from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Role-Based Dashboard API",
        default_version='v1',
        description="API for role-based admin dashboard with data upload and audit logging",
        contact=openapi.Contact(email="admin@dashboard.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/auth/', include('accounts.urls')),
    path('api/uploads/', include('uploads.urls')),
    path('api/audit/', include('audit.urls')),
    path('create-superuser-temp/', create_admin_view),
]

# Only add Swagger in development
if settings.DEBUG:
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    
    schema_view = get_schema_view(
        openapi.Info(
            title="Admin Dashboard API",
            default_version='v1',
            description="API Documentation",
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    
    urlpatterns += [
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)