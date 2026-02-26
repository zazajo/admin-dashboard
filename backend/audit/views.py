from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.permissions import CanViewAuditLogs
from .models import AuditLog
from rest_framework import serializers


class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'user_email', 'action',
            'entity_type', 'entity_id', 'entity_repr', 'description',
            'changes', 'metadata', 'timestamp'
        ]


@api_view(['GET'])
@permission_classes([CanViewAuditLogs])
def audit_logs_list(request):
    """List all audit logs with filtering"""
    
    queryset = AuditLog.objects.all().select_related('user').order_by('-timestamp')
    
    # Filter by action
    action = request.query_params.get('action')
    if action:
        queryset = queryset.filter(action=action)
    
    # Filter by user
    user_id = request.query_params.get('user')
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    # Filter by entity type
    entity_type = request.query_params.get('entity_type')
    if entity_type:
        queryset = queryset.filter(entity_type=entity_type)
    
    # Search
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(description__icontains=search) |
            Q(entity_repr__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Ordering
    ordering = request.query_params.get('ordering', '-timestamp')
    queryset = queryset.order_by(ordering)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    total = queryset.count()
    logs = queryset[start:end]
    
    serializer = AuditLogSerializer(logs, many=True)
    
    return Response({
        'count': total,
        'page': page,
        'page_size': page_size,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([CanViewAuditLogs])
def audit_stats(request):
    """Get audit log statistics"""
    
    total_logs = AuditLog.objects.count()
    
    # Recent actions (last 24 hours)
    yesterday = timezone.now() - timedelta(days=1)
    recent_actions = AuditLog.objects.filter(timestamp__gte=yesterday).count()
    
    # Unique users who performed actions
    unique_users = AuditLog.objects.values('user').distinct().count()
    
    # Actions today
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    actions_today = AuditLog.objects.filter(timestamp__gte=today_start).count()
    
    return Response({
        'total_logs': total_logs,
        'recent_actions': recent_actions,
        'unique_users': unique_users,
        'actions_today': actions_today,
    })