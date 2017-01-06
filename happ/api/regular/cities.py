from django.utils.translation import ugettext_lazy as _

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import City
from happ.serializers import CitySerializer


class CityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = CitySerializer
    queryset = City.objects.filter(is_active=True)
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('name', )

    @detail_route(methods=['post'], url_path='set')
    def set(self, request, id=None, *args, **kwargs):
        user = request.user
        try:
            city = City.objects.get(id=id)
        except City.DoesNotExist:
            return Response(
                {'error_message': _('Such city does not exist.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.settings.city = city
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['post'], url_path='nearest')
    def nearest(self, request, *args, **kwargs):
        if 'center' not in request.data:
            return Response(
                {'error_message': _('Center was not provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        city = City.get_nearest(request.data['center'])
        serializer = self.get_serializer(city)
        return Response(serializer.data)
