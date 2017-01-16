import datetime
import dateutil
import json
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.utils import store_file, string_to_date, string_to_time, daterange, date_to_string
from happ.models import Event, User, LogEntry
from happ.filters import EventFilter
from happ.policies import StaffPolicy
from happ.decorators import patch_queryset, patch_order, patch_pagination_class, patch_filter_class, log_entry
from happ.serializers import EventAdminSerializer


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = EventAdminSerializer
    filter_backends = (filters.MongoSearchFilter, filters.MongoFilterBackend,)
    search_fields = ('title', )
    filter_class = EventFilter
    queryset = Event.objects.all().order_by('-date_created')

    def get_queryset(self):
        queryset = super(EventViewSet, self).get_queryset()
        if self.request.user.role == User.MODERATOR:
            queryset = queryset.filter(city=self.request.user.assigned_city)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        response = super(EventViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = '/admin/events/detail.html'
        return response

    @patch_order({'default': ('datetimes__0__date', 'datetimes__0__start_time',)})
    def list(self, request, *args, **kwargs):
        response = super(EventViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/events/list.html'
        response.data['page'] = int(request.GET.get('page', 1))
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @log_entry(LogEntry.ADDITION, Event)
    def create(self, request, *args, **kwargs):
        """
        Creates event
        divides start_datetime into start_date and start_time
        divides end_datetime into end_date and end_time
        - launches celery tasks for translation
        """
        request.data._mutable = True # needs to be refined
        if 'title' not in request.data or request.data['title'] == '':
            return Response(
                {'error_message': _('No title provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'city_id' not in request.data or request.data['city_id'] == '':
            return Response(
                {'error_message': _('No city provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'currency_id' not in request.data or request.data['currency_id'] == '':
            return Response(
                {'error_message': _('No currency provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if ('min_price' not in request.data or request.data['min_price'] == '') and \
           ('max_price' not in request.data or request.data['max_price'] == ''):
            return Response(
                {'error_message': _('Min_price or max_price should be provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'web_site' in request.data and request.data['web_site'] != '':
            web_site = request.data['web_site']
            if not web_site.startswith('http://'):
                if not web_site.startswith('https://'):
                    request.data['web_site'] = 'http://' + web_site

        if 'raw_datetimes' not in request.data:
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
            start_datetime = dateutil.parser.parse(request.data.pop('start_datetime'))
            end_datetime = dateutil.parser.parse(request.data.pop('end_datetime'))

            start_time = datetime.datetime.strftime(start_datetime, settings.TIME_STRING_FIELD_FORMAT)
            end_time = datetime.datetime.strftime(end_datetime, settings.TIME_STRING_FIELD_FORMAT)
            request.data['raw_datetimes'] = [{
                'date': date_to_string(date, settings.DATE_STRING_FIELD_FORMAT),
                'start_time': start_time,
                'end_time': end_time,
            } for date in daterange(start_datetime.date(), end_datetime.date())]
        else:
            request.data.setlist('raw_datetimes', json.loads(request.data['raw_datetimes']))
            for item in request.data.getlist('raw_datetimes'):
                if 'date' not in item or \
                   'start_time' not in item or \
                   'end_time' not in item:
                    return Response(
                        {'error_message': _('Wrong datetimes format provided.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    string_to_date(str(item['date']), settings.DATE_STRING_FIELD_FORMAT)
                    string_to_time(item['start_time'], settings.TIME_STRING_FIELD_FORMAT)
                    string_to_time(item['end_time'], settings.TIME_STRING_FIELD_FORMAT)
                except:
                    return Response(
                        {'error_message': _('Wrong datetimes format provided.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        # print request.data['close_on_start']
        # if request.data['close_on_start'] == 'on':
        #     request.data['close_on_start'] = True
        # else:
        #     request.data['close_on_start'] = False

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

    @log_entry(LogEntry.CHANGE, Event)
    def update(self, request, *args, **kwargs):
        """
        Updates event
        divides start_datetime into start_date and start_time
        divides end_datetime into end_date and end_time
        - launches celery tasks for translation
        """
        instance = self.get_object()
        request.data._mutable = True # needs to be refined
        if 'title' not in request.data or request.data['title'] == '':
            return Response(
                {'error_message': _('No title provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'city_id' not in request.data or request.data['city_id'] == '':
            return Response(
                {'error_message': _('No city provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'currency_id' not in request.data or request.data['currency_id'] == '':
            return Response(
                {'error_message': _('No currency provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if ('min_price' not in request.data or request.data['min_price'] == '') and \
           ('max_price' not in request.data or request.data['max_price'] == ''):
            return Response(
                {'error_message': _('Min_price or max_price should be provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'raw_datetimes' not in request.data:
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
            start_datetime = dateutil.parser.parse(request.data.pop('start_datetime'))
            end_datetime = dateutil.parser.parse(request.data.pop('end_datetime'))

            start_time = datetime.datetime.strftime(start_datetime, settings.TIME_STRING_FIELD_FORMAT)
            end_time = datetime.datetime.strftime(end_datetime, settings.TIME_STRING_FIELD_FORMAT)
            request.data['raw_datetimes'] = [{
                'date': date_to_string(date, settings.DATE_STRING_FIELD_FORMAT),
                'start_time': start_time,
                'end_time': end_time,
            } for date in daterange(start_datetime.date(), end_datetime.date())]
        else:
            request.data.setlist('raw_datetimes', json.loads(request.data['raw_datetimes']))
            for item in request.data.getlist('raw_datetimes'):
                if 'date' not in item or \
                   'start_time' not in item or \
                   'end_time' not in item:
                    return Response(
                        {'error_message': _('Wrong datetimes format provided.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    string_to_date(str(item['date']), settings.DATE_STRING_FIELD_FORMAT)
                    string_to_time(item['start_time'], settings.TIME_STRING_FIELD_FORMAT)
                    string_to_time(item['end_time'], settings.TIME_STRING_FIELD_FORMAT)
                except:
                    return Response(
                        {'error_message': _('Wrong datetimes format provided.')},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        #print request.data.get('close_on_start')
        if request.data.get('close_on_start') and (request.data.get('close_on_start') == 'on' or request.data.get('close_on_start')==1):
            request.data['close_on_start'] = True
        else:
            request.data['close_on_start'] = False

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

    @log_entry(LogEntry.DELETION, Event)
    def destroy(self, request, *args, **kwargs):
        return super(EventViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='moderation')
    @patch_queryset(lambda self, x: x.filter(status=Event.MODERATION))
    def moderation(self, request, *args, **kwargs):
        response = super(EventViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/events/list.html'
        if request.GET.get('notification'):
            response.template_name = 'admin/events/notification.html'
        response.data['page'] = request.GET.get('page', 1)
        return response

    @detail_route(methods=['post'], url_path='approve')
    @log_entry(LogEntry.APPROVAL, Event)
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.approve()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='reject')
    @log_entry(LogEntry.REJECTION, Event)
    def reject(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        instance = self.get_object()
        instance.reject(text=text, author=request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'], url_path='reject/form')
    def reject_form(self, request, *args, **kwargs):
        response = super(EventViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = 'admin/events/reject.html'
        return response

    @detail_route(methods=['post'], url_path='activate')
    @log_entry(LogEntry.ACTIVATION, Event)
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activate()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='deactivate')
    @log_entry(LogEntry.DEACTIVATION, Event)
    def deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deactivate()

        return Response(status=status.HTTP_204_NO_CONTENT)
