from rest_framework import mixins
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets

from happ.models import Country
from happ.serializers import CountrySerializer


class CountryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
