from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, Q
from django.utils import timezone
from accounts.permissions import CanUploadData, CanEditData, CanDeleteData, IsAdminOrManager
from .models import DataUpload, SupportingDocument, UploadedRecord
from .serializers import (
    DataUploadSerializer,
    DataUploadCreateSerializer,
    SupportingDocumentSerializer,
    UploadedRecordSerializer,
    UploadStatsSerializer
)
from .file_processor import FileProcessor
from audit.models import AuditLog


class DataUploadListView(generics.ListAPIView):
    """List all data uploads"""
    
    serializer_class = DataUploadSerializer
    permission_classes = [CanUploadData]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['file_name', 'uploaded_by__username']
    ordering_fields = ['created_at', 'status', 'total_rows']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = DataUpload.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by uploaded_by
        user_id = self.request.query_params.get('uploaded_by')
        if user_id:
            queryset = queryset.filter(uploaded_by_id=user_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset


class DataUploadCreateView(generics.CreateAPIView):
    """Upload a new CSV/Excel file"""
    
    serializer_class = DataUploadCreateSerializer
    permission_classes = [CanUploadData]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the DataUpload instance
        data_upload = DataUpload.objects.create(
            file=serializer.validated_data['file'],
            uploaded_by=request.user,
            status=DataUpload.Status.PENDING
        )
        
        # Process supporting documents if provided
        supporting_docs = request.FILES.getlist('supporting_documents')
        for doc_file in supporting_docs:
            SupportingDocument.objects.create(
                data_upload=data_upload,
                file=doc_file,
                uploaded_by=request.user
            )
        
        # Log the upload
        AuditLog.log_action(
            user=request.user,
            action=AuditLog.Action.UPLOAD,
            entity_type='DataUpload',
            entity_id=data_upload.id,
            entity_repr=data_upload.file_name,
            description=f'Uploaded file: {data_upload.file_name}',
            metadata={'file_size': data_upload.file_size}
        )
        
        # Return the created upload
        output_serializer = DataUploadSerializer(data_upload, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class DataUploadDetailView(generics.RetrieveAPIView):
    """Get details of a specific upload"""
    
    queryset = DataUpload.objects.all()
    serializer_class = DataUploadSerializer
    permission_classes = [CanUploadData]
    lookup_field = 'pk'


class DataUploadDeleteView(generics.DestroyAPIView):
    """Delete an upload"""
    
    queryset = DataUpload.objects.all()
    serializer_class = DataUploadSerializer
    permission_classes = [CanDeleteData]
    lookup_field = 'pk'
    
    def perform_destroy(self, instance):
        # Log the deletion
        AuditLog.log_delete(
            user=self.request.user,
            instance=instance,
            description=f'Deleted upload: {instance.file_name}'
        )
        instance.delete()


@api_view(['POST'])
@permission_classes([CanUploadData])
def preview_upload(request):
    """
    Preview uploaded file before processing
    Returns column info and sample data
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Read file
    df, error = FileProcessor.read_file(file)
    
    if error:
        return Response(
            {'error': error},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate DataFrame
    is_valid, validation_errors = FileProcessor.validate_dataframe(df)
    
    if not is_valid:
        return Response(
            {'error': 'File validation failed', 'validation_errors': validation_errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get preview data
    preview_data = FileProcessor.get_preview_data(df, max_rows=10)
    column_info = FileProcessor.get_column_info(df)
    
    return Response({
        'file_name': file.name,
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': column_info,
        'preview_data': preview_data,
    })


@api_view(['POST'])
@permission_classes([CanUploadData])
def process_upload(request, pk):
    """
    Process an uploaded file and create records
    """
    try:
        data_upload = DataUpload.objects.get(pk=pk)
    except DataUpload.DoesNotExist:
        return Response(
            {'error': 'Upload not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already processed
    if data_upload.status == DataUpload.Status.COMPLETED:
        return Response(
            {'error': 'Upload already processed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update status
    data_upload.status = DataUpload.Status.PROCESSING
    data_upload.save()
    
    try:
        # Read file
        df, error = FileProcessor.read_file(data_upload.file)
        
        if error:
            data_upload.status = DataUpload.Status.FAILED
            data_upload.error_message = error
            data_upload.save()
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process records
        valid_records, invalid_records = FileProcessor.process_dataframe(df)
        
        # Create UploadedRecord entries
        for record in valid_records + invalid_records:
            UploadedRecord.objects.create(
                data_upload=data_upload,
                row_number=record['row_number'],
                data=record['data'],
                is_valid=record['is_valid'],
                validation_errors=record['errors']
            )
        
        # Update upload statistics
        data_upload.total_rows = len(df)
        data_upload.processed_rows = len(valid_records)
        data_upload.error_rows = len(invalid_records)
        data_upload.status = DataUpload.Status.COMPLETED
        data_upload.completed_at = timezone.now()
        
        # Store error details if any
        if invalid_records:
            data_upload.error_details = {
                'invalid_rows': [r['row_number'] for r in invalid_records],
                'sample_errors': invalid_records[:5]  # First 5 errors
            }
        
        data_upload.save()
        
        # Log processing
        AuditLog.log_action(
            user=request.user,
            action=AuditLog.Action.UPDATE,
            entity_type='DataUpload',
            entity_id=data_upload.id,
            entity_repr=data_upload.file_name,
            description=f'Processed upload: {data_upload.file_name}',
            metadata={
                'total_rows': data_upload.total_rows,
                'processed_rows': data_upload.processed_rows,
                'error_rows': data_upload.error_rows
            }
        )
        
        serializer = DataUploadSerializer(data_upload, context={'request': request})
        return Response(serializer.data)
    
    except Exception as e:
        data_upload.status = DataUpload.Status.FAILED
        data_upload.error_message = str(e)
        data_upload.save()
        
        return Response(
            {'error': f'Processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([CanUploadData])
def upload_stats(request):
    """Get upload statistics"""
    
    uploads = DataUpload.objects.all()
    
    stats = {
        'total_uploads': uploads.count(),
        'completed_uploads': uploads.filter(status=DataUpload.Status.COMPLETED).count(),
        'failed_uploads': uploads.filter(status=DataUpload.Status.FAILED).count(),
        'pending_uploads': uploads.filter(
            Q(status=DataUpload.Status.PENDING) | Q(status=DataUpload.Status.PROCESSING)
        ).count(),
        'total_records_processed': uploads.aggregate(
            total=Sum('processed_rows')
        )['total'] or 0,
        'total_errors': uploads.aggregate(
            total=Sum('error_rows')
        )['total'] or 0,
    }
    
    serializer = UploadStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([CanUploadData])
def upload_records(request, pk):
    """Get records for a specific upload"""
    
    try:
        data_upload = DataUpload.objects.get(pk=pk)
    except DataUpload.DoesNotExist:
        return Response(
            {'error': 'Upload not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get records
    records = UploadedRecord.objects.filter(data_upload=data_upload)
    
    # Filter by validity
    valid_only = request.query_params.get('valid_only')
    if valid_only == 'true':
        records = records.filter(is_valid=True)
    elif valid_only == 'false':
        records = records.filter(is_valid=False)
    
    # Pagination
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    total = records.count()
    records = records[start:end]
    
    serializer = UploadedRecordSerializer(records, many=True)
    
    return Response({
        'count': total,
        'page': page,
        'page_size': page_size,
        'results': serializer.data
    })