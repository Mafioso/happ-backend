from django.utils.translation import ugettext_lazy as _

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework_mongoengine import viewsets

from happ.models import Currency
from happ.serializers import CurrencySerializer


class CurrencyViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()

    @detail_route(methods=['get'], url_path='set')
    def set(self, request, id=None, *args, **kwargs):
        user = request.user
        try:
            currency = Currency.objects.get(id=id)
        except Currency.DoesNotExist:
            return Response(
                {'error_message': _('Such currency does not exist.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.settings.currency = currency
        user.save()
        return Response(status=status.HTTP_200_OK)
