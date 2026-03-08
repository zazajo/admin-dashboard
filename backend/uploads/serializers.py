from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DataUpload, SupportingDocument, UploadedRecord
import os

User = get_user_model()


class SupportingDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PDF documents"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportingDocument
        fields = [
            'id', 'file', 'file_name', 'file_size', 'description',
            'uploaded_by', 'uploaded_by_name', 'created_at', 'file_url'
        ]
        read_only_fields = ['id', 'file_name', 'file_size', 'uploaded_by', 'created_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


class UploadedRecordSerializer(serializers.ModelSerializer):
    """Serializer for individual uploaded records"""
    
    class Meta:
        model = UploadedRecord
        fields = [
            'id', 'row_number', 'data', 'is_valid',
            'validation_errors', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataUploadSerializer(serializers.ModelSerializer):
    """Serializer for data uploads with related documents"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    supporting_documents = SupportingDocumentSerializer(many=True, read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DataUpload
        fields = [
            'id', 'file', 'file_name', 'file_size', 'status',
            'total_rows', 'processed_rows', 'error_rows',
            'error_message', 'error_details', 'success_rate',
            'uploaded_by', 'uploaded_by_name', 'uploaded_by_email',
            'created_at', 'updated_at', 'completed_at',
            'supporting_documents', 'file_url'
        ]
        read_only_fields = [
            'id', 'file_name', 'file_size', 'status',
            'total_rows', 'processed_rows', 'error_rows',
            'error_message', 'error_details', 'uploaded_by',
            'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


class DataUploadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new uploads"""
    
    class Meta:
        model = DataUpload
        fields = ['file']
    
    def validate_file(self, value):
        """Validate file extension and size"""
        # Check file extension
        ext = os.path.splitext(value.name)[1].lower()
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            )
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'File size exceeds maximum allowed size of {max_size / (1024*1024)}MB'
            )
        
        return value
    
    def validate_supporting_documents(self, value):
        """Validate PDF documents"""
        if not value:
            return value
        
        for doc in value:
            # Check file extension
            ext = os.path.splitext(doc.name)[1].lower()
            if ext != '.pdf':
                raise serializers.ValidationError(
                    f'Supporting documents must be PDF files. Got: {ext}'
                )
            
            # Check file size (max 10MB per PDF)
            max_size = 10 * 1024 * 1024
            if doc.size > max_size:
                raise serializers.ValidationError(
                    f'PDF file {doc.name} exceeds maximum allowed size of 10MB'
                )
        
        return value


class UploadStatsSerializer(serializers.Serializer):
    """Serializer for upload statistics"""
    
    total_uploads = serializers.IntegerField()
    completed_uploads = serializers.IntegerField()
    failed_uploads = serializers.IntegerField()
    pending_uploads = serializers.IntegerField()
    total_records_processed = serializers.IntegerField()
    total_errors = serializers.IntegerField()