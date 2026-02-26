from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles: Admin, Manager, Viewer
    """
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        VIEWER = 'VIEWER', 'Viewer'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text='User role determines access permissions'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager(self):
        """Check if user has manager role"""
        return self.role == self.Role.MANAGER
    
    @property
    def is_viewer(self):
        """Check if user has viewer role"""
        return self.role == self.Role.VIEWER
    
    def can_manage_users(self):
        """Only admins can manage users"""
        return self.is_admin
    
    def can_upload_data(self):
        """Admins and managers can upload data"""
        return self.is_admin or self.is_manager
    
    def can_edit_data(self):
        """Admins and managers can edit data"""
        return self.is_admin or self.is_manager
    
    def can_delete_data(self):
        """Only admins can delete data"""
        return self.is_admin
    
    def can_export_reports(self):
        """Admins and managers can export reports"""
        return self.is_admin or self.is_manager
    
    def can_view_audit_logs(self):
        """Admins and managers can view audit logs"""
        return self.is_admin or self.is_manager
    
    def clean(self):
        """Validate user data"""
        super().clean()
        
        # Ensure at least one admin exists
        if self.pk and self.role != self.Role.ADMIN:
            admin_count = User.objects.filter(role=self.Role.ADMIN, is_active=True).exclude(pk=self.pk).count()
            if admin_count == 0:
                raise ValidationError('There must be at least one active admin user.')