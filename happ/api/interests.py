from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from ..models import Interest
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
        try:
            interests = Interest.objects.filter(id__in=data)
        except Interest.DoesNotExist:
            return Response(
                {'error_message': _('Such city does not exist.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error_message': _('Bad data.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.interests = interests
        user.save()
        return Response(status=status.HTTP_200_OK)
