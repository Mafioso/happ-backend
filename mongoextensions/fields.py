import datetime
import dateutil

from django.conf import settings

from mongoengine.fields import StringField


class DateStringField(StringField):
    """
        A custom date field which stores date as YYYYMMDD string.
    """
    
    def __init__(self, format=None, **kwargs):
        self.format = format or settings.DATE_STRING_FIELD_FORMAT
        super(DateStringField, self).__init__(**kwargs)

    def validate(self, value):
        new_value = self.to_mongo(value)
        if not isinstance(new_value, (basestring)):
            self.error(u'cannot parse date "%s"' % value)

    def to_python(self, value):
        return datetime.datetime.strptime(self.to_mongo(value), self.format).date()

    def to_mongo(self, value):
        if value is None:
            return value
        if isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
            return datetime.datetime.strftime(datetime.datetime(value.year, value.month, value.day), self.format)
        if callable(value):
            return value()

        if not isinstance(value, basestring):
            return None

        # Attempt to parse a datetime:
        try:
            return datetime.datetime.strftime(dateutil.parser.parse(value), self.format)
        except (TypeError, ValueError):
            return None

    def prepare_query_value(self, op, value):
        return super(DateStringField, self).prepare_query_value(op, self.to_mongo(value))


class TimeStringField(StringField):
    """
        A custom date field which stores date as YYYYMMDD string.
    """
    
    def __init__(self, format=None, **kwargs):
        self.format = format or settings.TIME_STRING_FIELD_FORMAT
        super(TimeStringField, self).__init__(**kwargs)

    def validate(self, value):
        new_value = self.to_mongo(value)
        if not isinstance(new_value, (basestring)):
            self.error(u'cannot parse time "%s"' % value)

    def to_python(self, value):
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, datetime.datetime):
            return value.time()
        return datetime.datetime.strptime(value, self.format).time()

    def to_mongo(self, value):
        if value is None:
            return value
        if isinstance(value, datetime.time) or isinstance(value, datetime.datetime):
            return datetime.datetime.strftime(datetime.datetime(1900, 1, 1, value.hour, value.minute, value.second), self.format)
        if callable(value):
            return value()

        if not isinstance(value, basestring):
            return None

        # Attempt to parse a datetime:
        try:
            datetime.datetime.strptime(value, self.format)
            return value
        except (TypeError, ValueError):
            return None

    def prepare_query_value(self, op, value):
        return super(TimeStringField, self).prepare_query_value(op, self.to_mongo(value))
