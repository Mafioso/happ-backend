from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import Interest
from happ.decorators import patch_serializer_class, patch_queryset
from happ.serializers import InterestSerializer, InterestParentSerializer, InterestChildSerializer


class InterestViewSet(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    @list_route(methods=['get'], url_path='categories')
    @patch_queryset(lambda x: x.filter(parent=None))
    @patch_serializer_class(InterestParentSerializer)
    def categories(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        # response.template_name =
        return response

    @list_route(methods=['get'], url_path='children')
    @patch_queryset(lambda x: x.filter(parent__ne=None))
    @patch_serializer_class(InterestChildSerializer)
    def children(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        # response.template_name =
        return response
