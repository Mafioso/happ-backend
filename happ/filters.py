from rest_framework import fields

from mongoextensions.filters import filtersets, filters
from .models import Event, LogEntry


class EventFilter(filtersets.ModelFilterset):
    start_date = filters.ListItemFilter(list_field='datetimes', at2='date', lookup='gte')
    start_time = filters.ListItemFilter(list_field='datetimes', at2='start_time', lookup='gte')
    end_date = filters.ListItemFilter(list_field='datetimes', at2='date', lookup='lte')
    end_time = filters.ListItemFilter(list_field='datetimes', at2='end_time', lookup='lte')
    min_price = filters.IntegerFilter('gte')
    max_price = filters.IntegerFilter('lte')
    status = filters.ListFilter('in')
    type = filters.ListFilter('in')
    city = filters.ListFilter('in')
    interests = filters.ListFilter('in')

    class Meta:
        model = Event
        fields = [
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'min_price',
            'max_price',
            'status',
            'type',
        ]


class LogEntryFilter(filtersets.ModelFilterset):
    start_date = filters.DateTimeFilter(source='date_created', lookup='gte')
    end_date = filters.DateTimeFilter(source='date_created', lookup='lte')
    author = filters.ListFilter('in')

    class Meta:
        model = LogEntry
        fields = [
            'start_date',
            'end_date',
        ]
