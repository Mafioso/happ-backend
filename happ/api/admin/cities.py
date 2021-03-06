from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.admin.mixins import RoleMixin
from happ.models import City, User, LogEntry
from happ.policies import StaffPolicy, RootPolicy
from happ.decorators import patch_permission_classes, log_entry
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
    @log_entry(LogEntry.ADDITION, City)
    def create(self, request, *args, **kwargs):
        return super(CityViewSet, self).create(request, *args, **kwargs)

    @log_entry(LogEntry.CHANGE, City)
    def update(self, request, *args, **kwargs):
        return super(CityViewSet, self).update(request, *args, **kwargs)

    @log_entry(LogEntry.DELETION, City)
    def destroy(self, request, *args, **kwargs):
        return super(CityViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='create')
    @patch_permission_classes(( RootPolicy, ))
    def create_city_form(self, request, *args, **kwargs):
        response = super(CityViewSet, self).list(request, *args, **kwargs)
        response.data['api_key'] = settings.GOOGLE_BROWSER_KEY
        response.template_name = 'admin/city/create.html'
        return response

    @detail_route(methods=['post'], url_path='activate')
    @log_entry(LogEntry.ACTIVATION, City)
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activate()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='deactivate')
    @log_entry(LogEntry.DEACTIVATION, City)
    def deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deactivate()

        return Response(status=status.HTTP_204_NO_CONTENT)
