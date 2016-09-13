def patch_permission_classes(permission_classes):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            prev_permission_classes = self.permission_classes
            self.permission_classes = permission_classes
            self.check_permissions(request)
            rv = fn(self, request, *a, **kw)
            self.permission_classes = prev_permission_classes
            return rv
        return wrapper
    return decorator
