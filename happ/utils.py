import os
import uuid
import shutil
import dateutil
import datetime
import warnings
from calendar import timegm

from django.conf import settings

from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user):

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    from .serializers import UserPayloadSerializer
    payload = UserPayloadSerializer(user).data

    payload['exp'] = datetime.datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload

def store_file(temp_path, dest_root):
    if temp_path.find(dest_root) >= 0:
        return temp_path
    _, remaining_path = temp_path.split(settings.NGINX_TMP_UPLOAD_ROOT + '/')
    file_path = os.path.join(dest_root, remaining_path)
    shutil.move(temp_path, file_path)
    return file_path

def date_to_string(d, format):
    if d is None:
        return d
    if isinstance(d, datetime.date) or isinstance(d, datetime.datetime):
        return datetime.datetime.strftime(datetime.datetime(d.year, d.month, d.day), format)
    if callable(d):
        return d()

    if not isinstance(d, basestring):
        return None

    # Attempt to parse a datetime:
    try:
        return datetime.datetime.strftime(dateutil.parser.parse(d), format)
    except (TypeError, ValueError):
        return None

def string_to_date(s, format):
    return datetime.datetime.strptime(date_to_string(s, format), format).date()

def time_to_string(t, format):
    if t is None:
        return t
    if isinstance(t, datetime.time) or isinstance(t, datetime.datetime):
        return datetime.datetime.strftime(datetime.datetime(1900, 1, 1, t.hour, t.minute, t.second), format)
    if callable(t):
        return t()

    if not isinstance(t, basestring):
        return None

    # Attempt to parse a datetime:
    try:
        datetime.datetime.strptime(t, format)
        return t
    except (TypeError, ValueError):
        return None

def string_to_time(s, format):
    if isinstance(s, datetime.time):
        return s
    if isinstance(s, datetime.datetime):
        return s.time()
    return datetime.datetime.strptime(s, format).time()
