from django.db import models
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an admin.
    """
    message = 'You must be an admin to perform this action.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsAdminOrManager(permissions.BasePermission):
    """
    Permission class to check if user is admin or manager.
    """
    message = 'You must be an admin or manager to perform this action.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.is_manager)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin can do anything, others can only read.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow read-only for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins
        return request.user.is_admin


class CanManageUsers(permissions.BasePermission):
    """
    Permission to manage users (create, update, delete).
    Only admins can manage users.
    """
    message = 'Only admins can manage users.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_manage_users()
        )


class CanUploadData(permissions.BasePermission):
    """
    Permission to upload data.
    Admins and managers can upload.
    """
    message = 'You do not have permission to upload data.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_upload_data()
        )


class CanEditData(permissions.BasePermission):
    """
    Permission to edit data.
    Admins and managers can edit.
    """
    message = 'You do not have permission to edit data.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_edit_data()
        )


class CanDeleteData(permissions.BasePermission):
    """
    Permission to delete data.
    Only admins can delete.
    """
    message = 'Only admins can delete data.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_delete_data()
        )


class CanExportReports(permissions.BasePermission):
    """
    Permission to export reports.
    Admins and managers can export.
    """
    message = 'You do not have permission to export reports.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_export_reports()
        )


class CanViewAuditLogs(permissions.BasePermission):
    """
    Permission to view audit logs.
    Admins and managers can view logs.
    """
    message = 'You do not have permission to view audit logs.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_audit_logs()
        )
