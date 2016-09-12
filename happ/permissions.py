from django.utils.translation import ugettext_lazy as _

from rest_framework import permissions

from happ.models import User


class IsRoot(permissions.BasePermission):
    message = _('This action is not allowed.')

    def has_permission(self, request, view):
        return request.user.role == User.ROOT


class IsAdministrator(permissions.BasePermission):
    message = _('This action is not allowed.')

    def has_permission(self, request, view):
        return request.user.role >= User.ADMINISTRATOR


class IsModerator(permissions.BasePermission):
    message = _('This action is not allowed.')

    def has_permission(self, request, view):
        return request.user.role >= User.MODERATOR


class IsOrganizer(permissions.BasePermission):
    message = _('This action is not allowed.')

    def has_permission(self, request, view):
        return request.user.role >= User.ORGANIZER


class IsOwner(permissions.BasePermission):
    message = _('This action is not allowed.')

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author

