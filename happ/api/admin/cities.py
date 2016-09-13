from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import City
from happ.serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('name', )
