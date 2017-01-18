# -*- coding: utf-8 -*-

from django.template.library import Library
from django.conf import settings

from ..models import Event, User, LogEntry

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
def paginate(number, page=1):
    x = ((number-1)/settings.PAGE_SIZE)+1
    page = int(page)
    if x < 10:
        return range(1,x+1)
    if page >= 6 and page < x-5:
        return range(page-5, page+5)
    elif page >= 6 and page >= x-5:
        return range(x-10, x+1)
    return range(1, 10)

@register.filter(name='page_count')
def page_count(number):
    x = ((number-1)/settings.PAGE_SIZE)+1
    return x

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

@register.filter(name='event_type')
def event_type(type):
    if type == Event.NORMAL:
        return u"Стандартное"
    if type == Event.FEATURED:
        return u"Featured"
    if type == Event.ADS:
        return u"Ads"

@register.filter(name='gender')
def gender(type):
    return u"Мужской" if type == User.MALE else u"Женский"

@register.filter(name='role')
def role(role):
    if role == User.REGULAR:
        return u"Стандартный"
    if role == User.ORGANIZER:
        return u"Организатор"
    if role == User.MODERATOR:
        return u"Модератор"
    if role == User.ADMINISTRATOR:
        return u"Администратор"
    if role == User.ROOT:
        return u"Root"

@register.filter(name='get')
def get(d, attr):
    return d.get(attr, None)

@register.filter(name='getlist')
def getlist(d, attr):
    return d.getlist(attr, [])

@register.filter(name='split')
def split(s, delimeter=' '):
    if not s:
        return []
    return s.split(delimeter)

@register.simple_tag
def join_by_attr(the_list, attr_name, separator=', ', wrapper=''):
    return separator.join(wrapper+unicode(i[attr_name])+wrapper for i in the_list)

@register.filter(name='div')
def div(a, b):
    if b == 0:
        return 0
    return a / b

@register.filter(name='mult')
def mult(a, b):
    return a * b
