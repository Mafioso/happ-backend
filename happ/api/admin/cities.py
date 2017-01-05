from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.admin.mixins import RoleMixin
from happ.models import City, User
from happ.policies import StaffPolicy, RootPolicy
from happ.decorators import patch_permission_classes
from happ.serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = CitySerializer
    queryset = City.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('name', )

    def list(self, request, *args, **kwargs):
        response = super(CityViewSet, self).list(request, *args, **kwargs)
        response.data['roles'] = User.get_roles_dict()
        response.template_name = 'admin/city/list.html'
        if request.GET.get('select'):
            response.template_name = 'admin/city/select_city.html'
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super(CityViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = 'admin/city/edit.html'
        return response

    @patch_permission_classes(( RootPolicy, ))
    def create(self, request, *args, **kwargs):
        response = super(CityViewSet, self).create(request, *args, **kwargs)
        response.template_name = 'admin/city/success.html'
        return response

    @list_route(methods=['get'], url_path='create')
    @patch_permission_classes(( RootPolicy, ))
    def create_city_form(self, request, *args, **kwargs):
        response = super(CityViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/city/create.html'
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
