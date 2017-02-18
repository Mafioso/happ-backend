from rest_framework import status

from .models import LogEntry


def patch_serializer_class(serializer_class):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            prev_serializer_class = self.serializer_class
            self.serializer_class = serializer_class
            rv = fn(self, request, *a, **kw)
            self.serializer_class = prev_serializer_class
            return rv
        return wrapper
    return decorator

def patch_queryset(funct):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            prev_queryset = self.queryset
            self.queryset = funct(self, prev_queryset)
            rv = fn(self, request, *a, **kw)
            self.queryset = prev_queryset
            return rv
        return wrapper
    return decorator

def patch_order(sort_dict):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            prev_queryset = self.queryset
            order = request.GET.get('order')
            if order not in sort_dict:
                order = 'default'
            self.queryset = prev_queryset.order_by(*sort_dict[order])
            rv = fn(self, request, *a, **kw)
            self.queryset = prev_queryset
            return rv
        return wrapper
    return decorator

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

def patch_pagination_class(pagination_class):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            prev_pagination_class = self.pagination_class
            self.pagination_class = pagination_class
            rv = fn(self, request, *a, **kw)
            self.pagination_class = prev_pagination_class
            return rv
        return wrapper
    return decorator

def patch_filter_class(filter_class):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            prev_filter_class = self.filter_class
            self.filter_class = filter_class
            rv = fn(self, request, *a, **kw)
            self.filter_class = prev_filter_class
            return rv
        return wrapper
    return decorator

def log_entry(flag, cls):

    def decorator(fn):
        def wrapper(self, request, *a, **kw):
            if flag in (
                LogEntry.ADDITION,
                LogEntry.CHANGE,
            ):
                rv = fn(self, request, *a, **kw)
                if status.is_success(rv.status_code):
                    entity = cls.objects.get(id=rv.data['id'])
                    LogEntry.objects.create(entity=entity, flag=flag, author=request.user, data={attr: getattr(entity, attr) for attr in cls.log_attrs})
                return rv
            if flag in (
                LogEntry.DELETION,
                LogEntry.APPROVAL,
                LogEntry.REJECTION,
                LogEntry.ACTIVATION,
                LogEntry.DEACTIVATION,
                LogEntry.REPLY,
            ):
                entity = self.get_object()
                rv = fn(self, request, *a, **kw)
                if status.is_success(rv.status_code):
                    LogEntry.objects.create(entity=entity, flag=flag, author=request.user, data={attr: getattr(entity, attr) for attr in cls.log_attrs})
                return rv
        return wrapper
    return decorator
