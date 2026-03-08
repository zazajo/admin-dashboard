from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import os

User = get_user_model()


class DataUpload(models.Model):
    """
    Model for tracking data uploads (CSV/Excel files).
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='data_uploads'
    )
    
    file = models.FileField(
        upload_to='uploads/data/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['csv', 'xlsx', 'xls']
        )],
        help_text='CSV or Excel file'
    )
    
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)
    
    error_message = models.TextField(blank=True, null=True)
    error_details = models.JSONField(
        default=dict,
        blank=True,
        help_text='Detailed error information for failed rows'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Data Upload'
        verbose_name_plural = 'Data Uploads'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['uploaded_by']),
        ]
    
    def __str__(self):
        return f"{self.file_name} - {self.status} ({self.uploaded_by.username})"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = os.path.basename(self.file.name)
            if hasattr(self.file.file, 'size'):
                self.file_size = self.file.file.size
        super().save(*args, **kwargs)
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_rows == 0:
            return 0
        return round((self.processed_rows / self.total_rows) * 100, 2)


class SupportingDocument(models.Model):
    """
    Model for PDF documents attached to data uploads.
    """
    
    data_upload = models.ForeignKey(
        DataUpload,
        on_delete=models.CASCADE,
        related_name='supporting_documents'
    )
    
    file = models.FileField(
        upload_to='uploads/documents/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf']
        )],
        help_text='PDF document'
    )
    
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    description = models.TextField(blank=True)
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Supporting Document'
        verbose_name_plural = 'Supporting Documents'
    
    def __str__(self):
        return f"{self.file_name} (Upload #{self.data_upload.id})"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = os.path.basename(self.file.name)
            if hasattr(self.file.file, 'size'):
                self.file_size = self.file.file.size
        super().save(*args, **kwargs)


class UploadedRecord(models.Model):
    """
    Model for individual records from uploaded CSV/Excel files.
    This is a flexible model - adjust fields based on your actual data structure.
    """
    
    data_upload = models.ForeignKey(
        DataUpload,
        on_delete=models.CASCADE,
        related_name='records'
    )
    
    # Example fields - customize based on your needs
    row_number = models.PositiveIntegerField()
    data = models.JSONField(help_text='Row data as JSON')
    
    # Validation
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(
        default=list,
        blank=True,
        help_text='List of validation errors'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_records'
    )
    
    class Meta:
        ordering = ['row_number']
        verbose_name = 'Uploaded Record'
        verbose_name_plural = 'Uploaded Records'
        indexes = [
            models.Index(fields=['data_upload', 'row_number']),
            models.Index(fields=['is_valid']),
        ]
        unique_together = [['data_upload', 'row_number']]
    
    def __str__(self):
        return f"Record #{self.row_number} from Upload #{self.data_upload.id}"