from rest_framework import permissions
from .models import Role


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsNGO(permissions.BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.role and profile.role.name == 'ngo')


class IsVolunteer(permissions.BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.role and profile.role.name == 'volunteer')
