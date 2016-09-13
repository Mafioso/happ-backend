from restfw_composed_permissions.base import (BaseComposedPermision, And, Or)

from . import permissions


class StaffPolicy(BaseComposedPermision):
    def global_permission_set(self):
        return And(permissions.IsAuthenticated, permissions.IsStaff)

    def object_permission_set(self):
        return And(permissions.IsAuthenticated, permissions.IsStaff)
