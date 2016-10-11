from mongoextensions.filters import filtersets, filters
from .models import Event


class EventFilter(filtersets.ModelFilterset):
    start_date = filters.CharFilter('gte')
    start_time = filters.CharFilter('gte')
    end_date = filters.CharFilter('lte')
    end_time = filters.CharFilter('lte')
    min_price = filters.IntegerFilter('gte')
    max_price = filters.IntegerFilter('lte')

    class Meta:
        model = Event
        fields = ['start_date', 'start_time', 'end_date', 'end_time', 'min_price', 'max_price']