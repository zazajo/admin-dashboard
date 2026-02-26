from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {
            'fields': ('role',)
        }),
        ('Important Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    # Override to set default role when creating user in admin
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new user
            if not obj.role:
                obj.role = User.Role.VIEWER
        super().save_model(request, obj, form, change)