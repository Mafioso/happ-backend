from restfw_composed_permissions.base import (BaseComposedPermision, And, Or)

from . import permissions


class StaffPolicy(BaseComposedPermision):
    def global_permission_set(self):
        return And(permissions.IsAuthenticated, permissions.IsStaff)

    def object_permission_set(self):
        return And(permissions.IsAuthenticated, permissions.IsStaff)


class RootPolicy(BaseComposedPermision):
    def global_permission_set(self):
        return And(permissions.IsAuthenticated, permissions.IsRoot)

    def object_permission_set(self):
        return And(permissions.IsAuthenticated, permissions.IsRoot)


class RootAdministratorPolicy(BaseComposedPermision):
    def global_permission_set(self):
        return And(permissions.IsAuthenticated, Or(permissions.IsRoot, permissions.IsAdministrator,))

    def object_permission_set(self):
        return And(permissions.IsAuthenticated, Or(permissions.IsRoot, permissions.IsAdministrator,))
