from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """Allow staff/admins full access; everyone else may only touch their own record."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role == 'admin':
            return True
        return obj == request.user
