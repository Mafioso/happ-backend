from rest_framework_mongoengine import viewsets

from ..models import City
from ..serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()
