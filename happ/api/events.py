import datetime
import dateutil

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets

from ..tasks import translate_event
from ..models import Event
from ..serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Creates event
        divides start_datetime into start_date and start_time
        divides end_datetime into end_date and end_time
        - launches celery tasks for translation
        """
        if 'title' not in request.data:
            return Response(
                {'error_message': _('No title provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'city_id' not in request.data:
            return Response(
                {'error_message': _('No city provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'currency_id' not in request.data:
            return Response(
                {'error_message': _('No currency provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'start_datetime' not in request.data:
            return Response(
                {'error_message': _('No start_datetime provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'end_datetime' not in request.data:
            return Response(
                {'error_message': _('No end_datetime provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'min_price' not in request.data and 'max_price' not in request.data:
            return Response(
                {'error_message': _('Min_price or max_price should be provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        start_datetime = request.data.pop('start_datetime')
        end_datetime = request.data.pop('end_datetime')
        request.data['start_date'] = datetime.datetime.strftime(dateutil.parser.parse(start_datetime), settings.DATE_STRING_FIELD_FORMAT)
        request.data['start_time'] = datetime.datetime.strftime(dateutil.parser.parse(start_datetime), settings.TIME_STRING_FIELD_FORMAT)
        request.data['end_date'] = datetime.datetime.strftime(dateutil.parser.parse(end_datetime), settings.DATE_STRING_FIELD_FORMAT)
        request.data['end_time'] = datetime.datetime.strftime(dateutil.parser.parse(end_datetime), settings.TIME_STRING_FIELD_FORMAT)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            for language in settings.HAPP_LANGUAGES:
                translate_event.delay(event=serializer.data, target=language)

            return Response(status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
