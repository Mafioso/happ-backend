from django.utils.translation import ugettext_lazy as _

from restfw_composed_permissions.base import BasePermissionComponent

from happ.models import User


class IsAuthenticated(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_permission(self, permission, request, view):
        return request.user and request.user.is_authenticated


class IsRoot(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_permission(self, permission, request, view):
        return request.user.role == User.ROOT


class IsAdministrator(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_permission(self, permission, request, view):
        return request.user.role == User.ADMINISTRATOR


class IsModerator(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_permission(self, permission, request, view):
        return request.user.role == User.MODERATOR


class IsStaff(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_permission(self, permission, request, view):
        return request.user.role >= User.MODERATOR


class IsOrganizer(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_permission(self, permission, request, view):
        return request.user.role == User.ORGANIZER


class IsOwner(BasePermissionComponent):
    message = _('This action is not allowed.')

    def has_object_permission(self, permission, request, view, obj):
        return request.user == obj.author

