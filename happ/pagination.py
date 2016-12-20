from collections import OrderedDict

from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class SolidPagination(BasePagination):
    """
    No pagination actually. It returns whole data, but wraps it as object with `results` key.
    """

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        return list(queryset)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('results', data)
        ]))

