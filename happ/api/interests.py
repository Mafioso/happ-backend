from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from ..models import Interest, CityInterests, User
from ..serializers import InterestSerializer


class InterestViewSet(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = Interest.objects.all()
    pagination_class = None
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
            interests = Interest.objects.filter(id__in=data)
        except Interest.DoesNotExist:
            return Response(
                {'error_message': _('Such city does not exist.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error_message': _('Invalid data.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated = User.objects(id=user.id, interests__c=user.settings.city).update(set__interests__S__ins=interests)
        if not updated:
            city_interests = CityInterests(c=user.settings.city, ins=interests)
            user.update(push__interests=city_interests)
        return Response(status=status.HTTP_200_OK)
