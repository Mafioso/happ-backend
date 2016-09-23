from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import Interest
from happ.decorators import patch_serializer_class
from happ.serializers import InterestSerializer, InterestParentSerializer, InterestChildSerializer


class InterestViewSet(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    @list_route(methods=['get'], url_path='categories')
    @patch_serializer_class(InterestParentSerializer)
    def categories(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(parent=None))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    @list_route(methods=['get'], url_path='children')
    @patch_serializer_class(InterestChildSerializer)
    def children(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(parent__ne=None))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
