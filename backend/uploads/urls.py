from django.urls import path
from .views import (
    DataUploadListView,
    DataUploadCreateView,
    DataUploadDetailView,
    DataUploadDeleteView,
    preview_upload,
    process_upload,
    upload_stats,
    upload_records,
)

urlpatterns = [
    # Upload management
    path('', DataUploadListView.as_view(), name='upload_list'),
    path('create/', DataUploadCreateView.as_view(), name='upload_create'),
    path('<int:pk>/', DataUploadDetailView.as_view(), name='upload_detail'),
    path('<int:pk>/delete/', DataUploadDeleteView.as_view(), name='upload_delete'),
    
    # Processing
    path('preview/', preview_upload, name='upload_preview'),
    path('<int:pk>/process/', process_upload, name='upload_process'),
    
    # Records
    path('<int:pk>/records/', upload_records, name='upload_records'),
    
    # Statistics
    path('stats/', upload_stats, name='upload_stats'),
]