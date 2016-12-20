from collections import OrderedDict

from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class SolidPagination(BasePagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    """
    # The default page size.
    # Defaults to `None`, meaning pagination is disabled.

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        self.request = request
        return list(queryset)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('results', data)
        ]))

