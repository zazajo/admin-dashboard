from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user data"""
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role', 'is_active'
        ]
    
    def validate_role(self, value):
        """Prevent removing the last admin"""
        user = self.instance
        if user.role == User.Role.ADMIN and value != User.Role.ADMIN:
            admin_count = User.objects.filter(
                role=User.Role.ADMIN,
                is_active=True
            ).exclude(pk=user.pk).count()
            
            if admin_count == 0:
                raise serializers.ValidationError(
                    'Cannot change role. There must be at least one active admin.'
                )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with additional info"""
    
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'created_at', 'permissions'
        ]
        read_only_fields = ['id', 'created_at', 'role']
    
    def get_permissions(self, obj):
        """Get user permissions based on role"""
        return {
            'can_manage_users': obj.can_manage_users(),
            'can_upload_data': obj.can_upload_data(),
            'can_edit_data': obj.can_edit_data(),
            'can_delete_data': obj.can_delete_data(),
            'can_export_reports': obj.can_export_reports(),
            'can_view_audit_logs': obj.can_view_audit_logs(),
        }