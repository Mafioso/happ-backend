import operator

from django.utils import six

from rest_framework import filters
from mongoengine.queryset.visitor import Q

from .filtersets import BaseFilterset, ModelFilterset


class MongoSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        base = queryset
        for search_term in search_terms:
            queries = [
                Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            queryset = queryset.filter(reduce(operator.or_, queries))

        return queryset


class MongoFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_class = getattr(view,'filter_class', None)

        if filter_class is None:
            return queryset

        if not issubclass(filter_class, BaseFilterset):
            raise TypeError("%s expects filter_class to be %s: %s" % (self.__class__.__qualname__, BaseFilterset.__qualname__, repr(filter_class)))

        if not hasattr(view,'get_queryset'):
            raise TypeError("%s expects view to have get_queryset method" % (self.__class__.__qualname__,))

        if issubclass(filter_class, ModelFilterset):
            fs_model = filter_class.Meta.model
            qs_model = view.get_queryset()._document
            if not issubclass(qs_model, fs_model):
                raise TypeError("filter and view document class mismatch: %s vs %s " % (fs_model.__qualname__, qs_model.__qualname__))

        filterset = filter_class(request.query_params)
        return filterset.filter_queryset(queryset)
