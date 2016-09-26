from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets
from rest_framework import status
from mongoextensions import filters
from happ.models import Interest
from happ.decorators import patch_serializer_class, patch_queryset
from happ.serializers import InterestSerializer, InterestParentSerializer, InterestChildSerializer


class InterestViewSet(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    def retrieve(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = 'admin/interest/edit.html'
        if request.GET.get('category'):
            response.template_name = 'admin/categories/edit.html'
        return response

    def list(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/interest/list.html'

        return response

    @list_route(methods=['get'], url_path='categories')
    @patch_queryset(lambda self, x: x.filter(parent=None))
    @patch_serializer_class(InterestParentSerializer)
    def categories(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        response.data['page'] = int(request.GET.get('page', 1))
        response.template_name = 'admin/categories/list.html'
        if request.GET.get('select'):
            response.template_name = 'admin/categories/select_category.html'
        return response

    @list_route(methods=['get'], url_path='children')
    @patch_queryset(lambda self, x: x.filter(parent__ne=None))
    @patch_serializer_class(InterestChildSerializer)
    def children(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        response.data['page'] = int(request.GET.get('page', 1))
        response.template_name = 'admin/interest/list.html'
        return response

    @list_route(methods=['get'], url_path='categories/create')
    def create_category_form(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/categories/create.html'
        return response

    @list_route(methods=['get'], url_path='create')
    def create_interest_form(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/interest/create.html'
        return response
