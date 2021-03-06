import datetime
import dateutil

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework_mongoengine import viewsets
from rest_framework.pagination import CursorPagination
from mongoengine.queryset.visitor import Q

from mongoextensions import filters
from happ.utils import store_file, string_to_date, string_to_time, daterange, date_to_string, time_to_string
from happ.models import Event, Complaint, User
from happ.filters import EventFilter, FeedFilter
from happ.pagination import SolidPagination
from happ.decorators import patch_queryset, patch_order, patch_pagination_class, patch_serializer_class, patch_filter_class
from happ.serializers import EventSerializer, FeedSerializer


def filter_organizer_feed(self, queryset):
        FALSE = (False, 'False', 'false', '0')
        request = self.request
        queryset = request.user.get_organizer_feed()

        active = request.query_params.get('active', True)
        not_active = request.query_params.get('not_active', True)
        moderation = request.query_params.get('moderation', True)
        rejected = request.query_params.get('rejected', True)
        finished = request.query_params.get('finished', True)

        if active in FALSE:
            queryset = queryset.filter(Q(status__in=[Event.MODERATION, Event.REJECTED]) | Q(status=Event.APPROVED, is_active__ne=True))
        if not_active in FALSE:
            queryset = queryset.filter(Q(status__in=[Event.MODERATION, Event.REJECTED]) | Q(status=Event.APPROVED, is_active__ne=False))
        if moderation in FALSE:
            queryset = queryset.filter(status__ne=Event.MODERATION)
        if rejected in FALSE:
            queryset = queryset.filter(status__ne=Event.REJECTED)
        if finished in FALSE:
            queryset = queryset.filter(
                Q(datetimes__date__gt=date_to_string(datetime.datetime.now().date(), settings.DATE_STRING_FIELD_FORMAT) ) |
                Q(datetimes__date    =date_to_string(datetime.datetime.now().date(), settings.DATE_STRING_FIELD_FORMAT), datetimes__end_time__gte=time_to_string(datetime.datetime.now().time(), settings.TIME_STRING_FIELD_FORMAT) )
            )
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    filter_backends = (filters.MongoSearchFilter, filters.MongoFilterBackend,)
    filter_class = EventFilter
    search_fields = ('title', 'description', )

    def retrieve(self, request, *args, **kwargs):
        response = super(EventViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = 'events/detail.html'
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
        if request.user.role < User.ORGANIZER:
            return Response(
                {'error_message': _('Only Organizer can create events.')},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        if 'min_price' not in request.data and 'max_price' not in request.data:
            return Response(
                {'error_message': _('Min_price or max_price should be provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'datetimes' not in request.data:
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
            request.data['datetimes'] = [{
                'date': date_to_string(date, settings.DATE_STRING_FIELD_FORMAT),
                'start_time': start_time,
                'end_time': end_time,
            } for date in daterange(start_datetime.date(), end_datetime.date())]
        else:
            for item in request.data['datetimes']:
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
        if instance.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user.role < User.ORGANIZER:
            return Response(
                {'error_message': _('Only Organizer can edit events.')},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        if 'min_price' not in request.data and 'max_price' not in request.data:
            return Response(
                {'error_message': _('Min_price or max_price should be provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'datetimes' not in request.data:
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
            request.data['datetimes'] = [{
                'date': date_to_string(date, settings.DATE_STRING_FIELD_FORMAT),
                'start_time': start_time,
                'end_time': end_time,
            } for date in daterange(start_datetime.date(), end_datetime.date())]
        else:
            for item in request.data['datetimes']:
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user.role < User.ORGANIZER:
            return Response(
                {'error_message': _('Only Organizer can delete events.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super(EventViewSet, self).destroy(request, *args, **kwargs)

    @detail_route(methods=['post'], url_path='copy')
    def copy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user.role < User.ORGANIZER:
            return Response(
                {'error_message': _('Only Organizer can copy events.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_instance = instance.copy()
        serializer = self.get_serializer(new_instance)
        # new_instance.translate()
        return Response(serializer.data)

    @detail_route(methods=['post'], url_path='upvote')
    def upvote(self, request, *args, **kwargs):
        instance = self.get_object()
        flag = instance.upvote(self.request.user)
        if not flag:
            return Response(
                {'error_message': _('User has already upvoted this event.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='downvote')
    def downvote(self, request, *args, **kwargs):
        instance = self.get_object()
        flag = instance.downvote(self.request.user)
        if not flag:
            return Response(
                {'error_message': _('User should upvote this event first.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='fav')
    def fav(self, request, *args, **kwargs):
        instance = self.get_object()
        flag = instance.add_to_favourites(self.request.user)
        if not flag:
            return Response(
                {'error_message': _('User has already added this event to favourites.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='unfav')
    def unfav(self, request, *args, **kwargs):
        instance = self.get_object()
        flag = instance.remove_from_favourites(self.request.user)
        if not flag:
            return Response(
                {'error_message': _('User should add this event to favourites first.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'], url_path='favourites')
    @patch_queryset(lambda self, x: self.request.user.get_favourites())
    def favourites(self, request, *args, **kwargs):
        return super(EventViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='feed')
    @patch_serializer_class(FeedSerializer)
    @patch_queryset(lambda self, x: self.request.user.get_feed(self.request))
    @patch_order({'default': ('datetimes__date', 'datetimes__start_time', )})
    @patch_filter_class(FeedFilter)
    def feed(self, request, *args, **kwargs):
        return super(EventViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='featured')
    @patch_queryset(lambda self, x: self.request.user.get_featured())
    @patch_order({'default': ('datetimes__0__date', 'datetimes__0__start_time', ), 'popular': ('datetimes__0__date', '-votes_num')})
    def featured(self, request, *args, **kwargs):
        return super(EventViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='organizer')
    @patch_queryset(filter_organizer_feed)
    @patch_order({'default': ('datetimes__0__date', 'datetimes__0__start_time', ), 'popular': ('datetimes__0__date', '-votes_num')})
    def organizer(self, request, *args, **kwargs):
        return super(EventViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'], url_path='explore')
    @patch_queryset(lambda self, x: self.request.user.get_explore())
    @patch_pagination_class(SolidPagination)
    def explore(self, request, *args, **kwargs):
        return super(EventViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['post'], url_path='map')
    @patch_queryset(lambda self, x: self.request.user.get_map_feed(self.request.data.get('center', None), self.request.data.get('radius', None)))
    @patch_pagination_class(SolidPagination)
    def map(self, request, *args, **kwargs):
        return super(EventViewSet, self).list(request, *args, **kwargs)

    @detail_route(methods=['post'], url_path='complaint')
    def complaint(self, request, *args, **kwargs):
        instance = self.get_object()
        Complaint.objects.create(text=request.data.get('text', ''),
                                 event=instance,
                                 author=self.request.user
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='activate')
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user.role < User.ORGANIZER:
            return Response(
                {'error_message': _('Only Organizer can activate events.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.activate()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='deactivate')
    def deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if request.user.role < User.ORGANIZER:
            return Response(
                {'error_message': _('Only Organizer can deactivate events.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.deactivate()

        return Response(status=status.HTTP_204_NO_CONTENT)
