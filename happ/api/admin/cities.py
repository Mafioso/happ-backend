from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import City
from happ.policies import StaffPolicy, RootPolicy
from happ.decorators import patch_permission_classes
from happ.serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = CitySerializer
    queryset = City.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('name', )

    @patch_permission_classes(( RootPolicy, ))
    def create(self, request, *args, **kwargs):
        return super(CityViewSet, self).create(request, *args, **kwargs)
