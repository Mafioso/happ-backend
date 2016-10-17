# -*- coding: utf-8 -*-

from django.template.library import Library
from django.conf import settings

from ..models import Event

register = Library()


@register.filter(is_safe=True)
def to_int(value, default='0'):

    try:
        return int(value)
    except ValueError:
        # quotient
        if not '/' in value:
            return default
        try:
            num, denom = map(int, value.split('/'))
            return float(num) / denom
        except ValueError:
            return default

@register.filter(name='paginate')
def paginate(number):
    x = ((number-1)/settings.PAGE_SIZE)+1
    if x>10:
        x=10
    return range(x)

@register.filter(name='page_counter')
def page_counter(number, page=1):
    return ((int(page)-1)*settings.PAGE_SIZE)+int(number)

@register.filter(name='event_status')
def event_status(status):
    if status == Event.MODERATION:
        return u"На модерации"
    if status == Event.APPROVED:
        return u"Утвержден"
    if status == Event.REJECTED:
        return u"Отклонен"
