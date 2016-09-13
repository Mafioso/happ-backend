from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import Interest
from happ.policies import StaffPolicy, RootAdministratorPolicy
from happ.decorators import patch_permission_classes
from happ.serializers import InterestSerializer


class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    @patch_permission_classes(( RootAdministratorPolicy, ))
    def create(self, request, *args, **kwargs):
        return super(InterestViewSet, self).create(request, *args, **kwargs)
