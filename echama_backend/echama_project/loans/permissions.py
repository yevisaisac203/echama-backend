from rest_framework import permissions

from groups.models import Membership


class IsGroupMember(permissions.BasePermission):
    """Any group member may view a loan; only the requester (while pending) or a
    group admin/staff may delete it. Decided loans are a permanent record."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.role == 'admin':
            return True

        if request.method == 'DELETE':
            if obj.status != 'pending':
                return False
            is_group_admin = Membership.objects.filter(group=obj.group, user=user, is_admin=True).exists()
            return obj.member_id == user.id or is_group_admin

        return Membership.objects.filter(group=obj.group, user=user).exists()


class IsGroupAdminForDecision(permissions.BasePermission):
    """Only a group admin (or staff) may approve/decline a loan."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.role == 'admin':
            return True
        return Membership.objects.filter(group=obj.group, user=user, is_admin=True).exists()
