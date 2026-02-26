from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity_type', 'description', 'timestamp']
    list_filter = ['action', 'entity_type', 'timestamp']
    search_fields = ['user__username', 'description', 'entity_repr']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'