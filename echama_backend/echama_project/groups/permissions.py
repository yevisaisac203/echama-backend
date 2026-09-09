from rest_framework import permissions

from .models import Membership


class IsGroupAdmin(permissions.BasePermission):
    """Any member may read a group; only its admins (or staff) may write to it."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.role == 'admin':
            return True
        if request.method in permissions.SAFE_METHODS:
            return Membership.objects.filter(group=obj, user=user).exists()
        return Membership.objects.filter(group=obj, user=user, is_admin=True).exists()
