# backend/users/permissions.py
from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
            
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        return obj == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.is_superuser