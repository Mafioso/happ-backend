from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import Interest
from happ.policies import StaffPolicy
from happ.serializers import InterestSerializer


class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )
