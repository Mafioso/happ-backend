from rest_framework_mongoengine import viewsets

from ..models import Currency
from ..serializers import CurrencySerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
