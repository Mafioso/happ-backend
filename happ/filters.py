from rest_framework import fields

from mongoextensions.filters import filtersets, filters
from .models import Event, EventTime


class EventFilter(filtersets.ModelFilterset):
    start_date = filters.ListItemFilter(list_field='datetimes', at2='date', lookup='gte')
    start_time = filters.ListItemFilter(list_field='datetimes', at2='start_time', lookup='gte')
    end_date = filters.ListItemFilter(list_field='datetimes', at2='date', lookup='lte')
    end_time = filters.ListItemFilter(list_field='datetimes', at2='end_time', lookup='lte')
    min_price = filters.IntegerFilter('gte')
    max_price = filters.IntegerFilter('lte')
    status = filters.ListFilter('in')
    type = filters.ListFilter('in')

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

class EventOrganizerFilter(filtersets.LogicalModelFilterset):
    start_date = filters.ListItemFilter(list_field='datetimes', at2='date', lookup='gte')
    start_time = filters.ListItemFilter(list_field='datetimes', at2='start_time', lookup='gte')
    end_date = filters.ListItemFilter(list_field='datetimes', at2='date', lookup='lte')
    end_time = filters.ListItemFilter(list_field='datetimes', at2='end_time', lookup='lte')
    status = filters.ListFilter('in')
    is_active = filters.OtherFieldFilter(other_field='status', other_value=Event.APPROVED, base_filter=filters.ListFilter, base_field=fields.NullBooleanField, lookup='in')
    finished = filters.MethodFilter(fn=filters.get_finished, base_filter=filters.BooleanFilter, field_class=fields.NullBooleanField)

    def prepare_logic(self):
        # start_date & start_time & end_date & end_time & (status | is_active) & finished
        return {
            'or': [
                'status',
                'is_active',
            ],
            'and': [
                'start_date',
                'start_time',
                'end_date',
                'end_time',
                'finished',
            ]
        }

    class Meta:
        model = Event
        fields = [
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'status',
        ]
