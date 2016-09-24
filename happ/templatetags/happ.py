from django.template.library import Library
from django.conf import settings

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
    return range((number/settings.PAGE_SIZE)+1)
