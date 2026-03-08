from django.contrib import admin
from .models import DataUpload, SupportingDocument, UploadedRecord


@admin.register(DataUpload)
class DataUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'uploaded_by', 'status', 'total_rows', 'processed_rows', 'error_rows', 'created_at']
    list_filter = ['status', 'created_at', 'uploaded_by']
    search_fields = ['file_name', 'uploaded_by__username']
    readonly_fields = ['file_name', 'file_size', 'created_at', 'updated_at', 'completed_at', 'success_rate']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_name', 'file_size', 'uploaded_by')
        }),
        ('Processing Status', {
            'fields': ('status', 'total_rows', 'processed_rows', 'error_rows', 'success_rate')
        }),
        ('Error Details', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(SupportingDocument)
class SupportingDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'data_upload', 'uploaded_by', 'file_size', 'created_at']
    list_filter = ['created_at', 'uploaded_by']
    search_fields = ['file_name', 'description', 'uploaded_by__username']
    readonly_fields = ['file_name', 'file_size', 'created_at']


@admin.register(UploadedRecord)
class UploadedRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'data_upload', 'row_number', 'is_valid', 'created_at']
    list_filter = ['is_valid', 'created_at']
    search_fields = ['data_upload__file_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Record Information', {
            'fields': ('data_upload', 'row_number', 'is_valid')
        }),
        ('Data', {
            'fields': ('data',)
        }),
        ('Validation', {
            'fields': ('validation_errors',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('updated_by', 'created_at', 'updated_at')
        }),
    )