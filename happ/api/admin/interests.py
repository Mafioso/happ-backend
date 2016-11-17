from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import Interest
from happ.policies import StaffPolicy, RootAdministratorPolicy
from happ.decorators import patch_permission_classes, patch_serializer_class, patch_queryset
from happ.serializers import InterestSerializer, InterestParentSerializer, InterestChildSerializer


class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    @patch_permission_classes(( RootAdministratorPolicy, ))
    def create(self, request, *args, **kwargs):
        return super(InterestViewSet, self).create(request, *args, **kwargs)

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
    @patch_queryset(lambda self, x: x.filter(parent=None).order_by('-date_created'))
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

    @detail_route(methods=['post'], url_path='activate')
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activate()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='deactivate')
    def deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deactivate()

        return Response(status=status.HTTP_204_NO_CONTENT)
