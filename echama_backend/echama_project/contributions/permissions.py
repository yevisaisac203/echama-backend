from rest_framework import permissions

from groups.models import Membership


class IsGroupMember(permissions.BasePermission):
    """Any member of the contribution's group may view it; only group admins/staff may delete it."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.role == 'admin':
            return True
        if request.method == 'DELETE':
            return Membership.objects.filter(group=obj.group, user=user, is_admin=True).exists()
        return Membership.objects.filter(group=obj.group, user=user).exists()
