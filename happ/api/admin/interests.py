from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import Interest
from happ.serializers import InterestSerializer


class InterestViewSet(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    def list(self, request, *args, **kwargs):
        response = super(InterestViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/interest/list.html'
        return response
