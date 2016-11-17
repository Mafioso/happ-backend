from django.utils.translation import ugettext_lazy as _

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets
from mongoengine import Q

from mongoextensions import filters
from happ.models import Interest, CityInterests, User
from happ.serializers import InterestParentSerializer


class InterestViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = InterestParentSerializer
    queryset = Interest.objects.filter(is_active=True, parent=None)
    filter_backends = (filters.MongoSearchFilter, )
    search_fields = ('title', )

    @list_route(methods=['post'], url_path='set')
    def set(self, request, id=None, *args, **kwargs):
        user = request.user
        data = request.data
        if not user.settings.city:
            return Response(
                {'error_message': _('User should select city first.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            if 'all' in request.query_params:
                interests = Interest.objects.filter(Q(is_active=True) & (Q(is_global=True) | Q(local_cities=user.settings.city) ))
            else:
                interests = Interest.objects.filter(id__in=data)
        except Exception as e:
            return Response(
                {'error_message': _('Invalid data.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated = User.objects(id=user.id, interests__c=user.settings.city).update(set__interests__S__ins=interests)
        if not updated:
            city_interests = CityInterests(c=user.settings.city, ins=interests)
            user.update(push__interests=city_interests)
        return Response(status=status.HTTP_204_NO_CONTENT)
