from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class AuditLog(models.Model):
    """
    Comprehensive audit logging for all important actions.
    Tracks who did what, when, and what changed.
    """
    
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Created'
        UPDATE = 'UPDATE', 'Updated'
        DELETE = 'DELETE', 'Deleted'
        UPLOAD = 'UPLOAD', 'Uploaded'
        DOWNLOAD = 'DOWNLOAD', 'Downloaded'
        EXPORT = 'EXPORT', 'Exported'
        LOGIN = 'LOGIN', 'Logged In'
        LOGOUT = 'LOGOUT', 'Logged Out'
        PERMISSION_CHANGE = 'PERMISSION_CHANGE', 'Permission Changed'
        STATUS_CHANGE = 'STATUS_CHANGE', 'Status Changed'
    
    # Who performed the action
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text='User who performed the action'
    )
    
    # What action was performed
    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )
    
    # What entity was affected (generic relation)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional context
    entity_type = models.CharField(
        max_length=100,
        help_text='Type of entity affected (User, DataUpload, etc.)'
    )
    entity_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of the affected entity'
    )
    entity_repr = models.CharField(
        max_length=255,
        blank=True,
        help_text='String representation of the entity'
    )
    
    # Details of the change
    description = models.TextField(
        help_text='Human-readable description of what happened'
    )
    
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text='Detailed changes (old_value, new_value)'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata (IP address, user agent, etc.)'
    )
    
    # When it happened
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['entity_type', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} {self.get_action_display()} {self.entity_type} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, entity_type, entity_id=None, 
                   entity_repr=None, description=None, changes=None, 
                   metadata=None, content_object=None):
        """
        Convenience method to create audit log entries.
        
        Usage:
            AuditLog.log_action(
                user=request.user,
                action=AuditLog.Action.UPLOAD,
                entity_type='DataUpload',
                entity_id=upload.id,
                entity_repr=str(upload),
                description=f'Uploaded {upload.file_name}',
                metadata={'file_size': upload.file_size}
            )
        """
        return cls.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else '',
            entity_repr=entity_repr or '',
            description=description or f'{action} {entity_type}',
            changes=changes or {},
            metadata=metadata or {},
            content_object=content_object
        )
    
    @classmethod
    def log_login(cls, user, metadata=None):
        """Log user login"""
        return cls.log_action(
            user=user,
            action=cls.Action.LOGIN,
            entity_type='User',
            entity_id=user.id,
            entity_repr=user.username,
            description=f'{user.username} logged in',
            metadata=metadata
        )
    
    @classmethod
    def log_logout(cls, user, metadata=None):
        """Log user logout"""
        return cls.log_action(
            user=user,
            action=cls.Action.LOGOUT,
            entity_type='User',
            entity_id=user.id,
            entity_repr=user.username,
            description=f'{user.username} logged out',
            metadata=metadata
        )
    
    @classmethod
    def log_create(cls, user, instance, description=None):
        """Log object creation"""
        return cls.log_action(
            user=user,
            action=cls.Action.CREATE,
            entity_type=instance.__class__.__name__,
            entity_id=instance.pk,
            entity_repr=str(instance),
            description=description or f'Created {instance.__class__.__name__}',
            content_object=instance
        )
    
    @classmethod
    def log_update(cls, user, instance, changes=None, description=None):
        """Log object update with changes"""
        return cls.log_action(
            user=user,
            action=cls.Action.UPDATE,
            entity_type=instance.__class__.__name__,
            entity_id=instance.pk,
            entity_repr=str(instance),
            description=description or f'Updated {instance.__class__.__name__}',
            changes=changes,
            content_object=instance
        )
    
    @classmethod
    def log_delete(cls, user, instance, description=None):
        """Log object deletion"""
        return cls.log_action(
            user=user,
            action=cls.Action.DELETE,
            entity_type=instance.__class__.__name__,
            entity_id=instance.pk,
            entity_repr=str(instance),
            description=description or f'Deleted {instance.__class__.__name__}'
        )