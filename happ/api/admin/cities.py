from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import City
from happ.serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('name', )

    def list(self, request, *args, **kwargs):
        response = super(CityViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/city/list.html'
        return response

    def create(self, request, *args, **kwargs):
        response = super(CityViewSet, self).create(request, *args, **kwargs)
        response.template_name = 'admin/city/success.html'
        return response
