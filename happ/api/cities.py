from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework_mongoengine import viewsets

from ..models import City
from ..serializers import CitySerializer


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()

    @detail_route(methods=['get'], url_path='set')
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
        return Response(status=status.HTTP_200_OK)
