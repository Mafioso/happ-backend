from django.conf import settings

from happ import utils
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
        return utils.string_to_date(value, self.format)

    def to_mongo(self, value):
        return utils.date_to_string(value, self.format)

    def prepare_query_value(self, op, value):
        return super(DateStringField, self).prepare_query_value(op, self.to_mongo(value))


class TimeStringField(StringField):
    """
        A custom time field which stores time as HHMMSS string.
    """

    def __init__(self, format=None, **kwargs):
        self.format = format or settings.TIME_STRING_FIELD_FORMAT
        super(TimeStringField, self).__init__(**kwargs)

    def validate(self, value):
        new_value = self.to_mongo(value)
        if not isinstance(new_value, (basestring)):
            self.error(u'cannot parse time "%s"' % value)

    def to_python(self, value):
        return utils.string_to_time(value, self.format)

    def to_mongo(self, value):
        return utils.time_to_string(value, self.format)

    def prepare_query_value(self, op, value):
        return super(TimeStringField, self).prepare_query_value(op, self.to_mongo(value))
