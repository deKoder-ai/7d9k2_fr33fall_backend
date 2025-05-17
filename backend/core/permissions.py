# backend/core/permissions.py
from rest_framework import permissions
from users.permissions import IsOwnerOrAdmin

class IsOwnerOrAdminForExample(IsOwnerOrAdmin):
    pass