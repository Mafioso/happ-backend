import datetime
import dateutil

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets

from happ.utils import store_file, string_to_date, string_to_time
from happ.models import Event
from happ.policies import StaffPolicy
from happ.decorators import patch_queryset
from happ.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = super(EventViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = '/admin/events/detail.html'
        return response

    def list(self, request, *args, **kwargs):
        response = super(EventViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/events/list.html'
        response.data['page'] = request.GET.get('page', 1)
        return response

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
        start_datetime = dateutil.parser.parse(request.data.pop('start_datetime'))
        end_datetime = dateutil.parser.parse(request.data.pop('end_datetime'))

        request.data['images'] = map(lambda x: store_file(x), request.data.pop('images'))
        request.data['start_date'] = string_to_date(datetime.datetime.strftime(start_datetime, settings.DATE_STRING_FIELD_FORMAT), settings.DATE_STRING_FIELD_FORMAT)
        request.data['start_time'] = string_to_time(datetime.datetime.strftime(start_datetime, settings.TIME_STRING_FIELD_FORMAT), settings.TIME_STRING_FIELD_FORMAT)
        request.data['end_date'] = string_to_date(datetime.datetime.strftime(end_datetime, settings.DATE_STRING_FIELD_FORMAT), settings.DATE_STRING_FIELD_FORMAT)
        request.data['end_time'] = string_to_time(datetime.datetime.strftime(end_datetime, settings.TIME_STRING_FIELD_FORMAT), settings.TIME_STRING_FIELD_FORMAT)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """
        Updates event
        divides start_datetime into start_date and start_time
        divides end_datetime into end_date and end_time
        - launches celery tasks for translation
        """
        instance = self.get_object()
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
        start_datetime = dateutil.parser.parse(request.data.pop('start_datetime'))
        end_datetime = dateutil.parser.parse(request.data.pop('end_datetime'))

        request.data['start_date'] = string_to_date(datetime.datetime.strftime(start_datetime, settings.DATE_STRING_FIELD_FORMAT), settings.DATE_STRING_FIELD_FORMAT)
        request.data['start_time'] = string_to_time(datetime.datetime.strftime(start_datetime, settings.TIME_STRING_FIELD_FORMAT), settings.TIME_STRING_FIELD_FORMAT)
        request.data['end_date'] = string_to_date(datetime.datetime.strftime(end_datetime, settings.DATE_STRING_FIELD_FORMAT), settings.DATE_STRING_FIELD_FORMAT)
        request.data['end_time'] = string_to_time(datetime.datetime.strftime(end_datetime, settings.TIME_STRING_FIELD_FORMAT), settings.TIME_STRING_FIELD_FORMAT)

        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @list_route(methods=['post'], url_path='upload')
    def upload(self, request, *args, **kwargs):
        return Response(request.data.getlist('images', []))

    @list_route(methods=['get'], url_path='moderation')
    @patch_queryset(lambda self, x: x.filter(status=Event.MODERATION))
    def moderation(self, request, *args, **kwargs):
        response = super(EventViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/events/list.html'
        response.data['page'] = request.GET.get('page', 1)
        return response

    @detail_route(methods=['post'], url_path='approve')
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.approve()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='reject')
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.reject()

        return Response(status=status.HTTP_204_NO_CONTENT)
