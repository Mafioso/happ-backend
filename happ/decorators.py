from rest_framework import filters


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

