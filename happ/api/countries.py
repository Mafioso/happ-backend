from rest_framework import mixins
from rest_framework_mongoengine import viewsets

from ..models import Country
from ..serializers import CountrySerializer


class CountryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    pagination_class = None
