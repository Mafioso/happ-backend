from rest_framework_mongoengine import viewsets

from ..models import Interest
from ..serializers import InterestSerializer


class InterestViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    pagination_class = None
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
