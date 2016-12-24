from mongoextensions.filters import filtersets, filters
from .models import Event, EventTime


class EventFilter(filtersets.ModelFilterset):
    start_date = filters.OtherEntityFilter(entity=EventTime, entity_field='date', reference_field='event', lookup='gte')
    start_time = filters.OtherEntityFilter(entity=EventTime, entity_field='start_time', reference_field='event', lookup='gte')
    end_date = filters.OtherEntityFilter(entity=EventTime, entity_field='date', reference_field='event', lookup='lte')
    end_time = filters.OtherEntityFilter(entity=EventTime, entity_field='end_time', reference_field='event', lookup='lte')
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
