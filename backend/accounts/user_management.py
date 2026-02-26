from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .permissions import CanManageUsers
from audit.models import AuditLog

User = get_user_model()


class UserListView(generics.ListAPIView):
    """
    List all users with search and filtering.
    Only admins can access this.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'role', 'created_at', 'is_active']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class UserCreateView(generics.CreateAPIView):
    """
    Create a new user.
    Only admins can create users.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [CanManageUsers]
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Log the creation
        AuditLog.log_create(
            user=self.request.user,
            instance=user,
            description=f'Admin {self.request.user.username} created user {user.username} with role {user.get_role_display()}'
        )


class UserDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific user.
    Only admins can access this.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]
    lookup_field = 'pk'


class UserUpdateView(generics.UpdateAPIView):
    """
    Update a user's information.
    Only admins can update users.
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [CanManageUsers]
    lookup_field = 'pk'
    
    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_data = {
            'email': old_instance.email,
            'first_name': old_instance.first_name,
            'last_name': old_instance.last_name,
            'role': old_instance.role,
            'is_active': old_instance.is_active,
        }
        
        user = serializer.save()
        
        # Track what changed
        changes = {}
        for field in ['email', 'first_name', 'last_name', 'role', 'is_active']:
            old_val = old_data[field]
            new_val = getattr(user, field)
            if old_val != new_val:
                changes[field] = {
                    'old': old_val,
                    'new': new_val
                }
        
        # Log the update
        if changes:
            AuditLog.log_update(
                user=self.request.user,
                instance=user,
                changes=changes,
                description=f'Admin {self.request.user.username} updated user {user.username}'
            )


class UserDeleteView(generics.DestroyAPIView):
    """
    Delete a user (soft delete by setting is_active=False).
    Only admins can delete users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]
    lookup_field = 'pk'
    
    def perform_destroy(self, instance):
        # Prevent deleting the last admin
        if instance.is_admin:
            admin_count = User.objects.filter(role=User.Role.ADMIN, is_active=True).count()
            if admin_count <= 1:
                from rest_framework.exceptions import ValidationError
                raise ValidationError('Cannot delete the last admin user.')
        
        # Soft delete
        instance.is_active = False
        instance.save()
        
        # Log the deletion
        AuditLog.log_action(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            entity_type='User',
            entity_id=instance.id,
            entity_repr=instance.username,
            description=f'Admin {self.request.user.username} deactivated user {instance.username}'
        )


@api_view(['POST'])
def activate_user(request, pk):
    """
    Activate a deactivated user.
    Only admins can activate users.
    """
    if not request.user.can_manage_users():
        return Response(
            {'error': 'Permission denied.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(pk=pk)
        user.is_active = True
        user.save()
        
        # Log the activation
        AuditLog.log_action(
            user=request.user,
            action=AuditLog.Action.STATUS_CHANGE,
            entity_type='User',
            entity_id=user.id,
            entity_repr=user.username,
            description=f'Admin {request.user.username} activated user {user.username}',
            changes={'is_active': {'old': False, 'new': True}}
        )
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def user_stats(request):
    """
    Get user statistics.
    Only admins can access this.
    """
    if not request.user.can_manage_users():
        return Response(
            {'error': 'Permission denied.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'admins': User.objects.filter(role=User.Role.ADMIN, is_active=True).count(),
        'managers': User.objects.filter(role=User.Role.MANAGER, is_active=True).count(),
        'viewers': User.objects.filter(role=User.Role.VIEWER, is_active=True).count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)