from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, 
    UserCreateSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    LoginSerializer
)
from audit.models import AuditLog

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user data in response"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = UserProfileSerializer(self.user).data
        
        # Log the login
        AuditLog.log_login(
            user=self.user,
            metadata={
                'ip_address': self.context.get('request').META.get('REMOTE_ADDR'),
                'user_agent': self.context.get('request').META.get('HTTP_USER_AGENT'),
            }
        )
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with audit logging"""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    Only admins can create users (controlled by frontend/permissions).
    For public registration, remove permission_classes.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]  # Change to [IsAdmin] if only admins should create users
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Log the registration
        AuditLog.log_create(
            user=self.request.user if self.request.user.is_authenticated else None,
            instance=user,
            description=f'New user registered: {user.username}'
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def perform_update(self, serializer):
        old_data = {
            'email': self.request.user.email,
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
        }
        
        user = serializer.save()
        
        # Track what changed
        changes = {}
        for field in ['email', 'first_name', 'last_name']:
            if old_data[field] != getattr(user, field):
                changes[field] = {
                    'old': old_data[field],
                    'new': getattr(user, field)
                }
        
        # Log the update
        if changes:
            AuditLog.log_update(
                user=self.request.user,
                instance=user,
                changes=changes,
                description=f'User {user.username} updated their profile'
            )


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Set new password
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            # Log the password change
            AuditLog.log_action(
                user=request.user,
                action=AuditLog.Action.UPDATE,
                entity_type='User',
                entity_id=request.user.id,
                entity_repr=request.user.username,
                description=f'{request.user.username} changed their password'
            )
            
            return Response({
                'message': 'Password changed successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout user by blacklisting their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log the logout
            AuditLog.log_logout(
                user=request.user,
                metadata={
                    'ip_address': request.META.get('REMOTE_ADDR'),
                }
            )
            
            return Response({
                'message': 'Logged out successfully.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth(request):
    """
    Check if user is authenticated and return their data.
    Useful for frontend to verify token validity.
    """
    return Response({
        'authenticated': True,
        'user': UserProfileSerializer(request.user).data
    })