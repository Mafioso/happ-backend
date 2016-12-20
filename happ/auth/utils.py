import jwt
import random
import hashlib

from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _

from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings

from ..models import User


def get_jwt_value_from_cookies(cookies):
    auth = cookies.get(settings.SESSION_COOKIE_NAME)
    if not auth:
        return None
    auth = auth.split()
    auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

    if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
        return None

    if len(auth) == 1:
        msg = _('Invalid Authorization header. No credentials provided.')
        raise exceptions.AuthenticationFailed(msg)
    elif len(auth) > 2:
        msg = _('Invalid Authorization header. Credentials string '
                'should not contain spaces.')
        raise exceptions.AuthenticationFailed(msg)

    return auth[1]

def check_payload(token):
    try:
        payload = api_settings.JWT_DECODE_HANDLER(token)
    except jwt.ExpiredSignature:
        return False
    except jwt.DecodeError:
        return False

    return payload

def check_user(payload):
        username = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER(payload)

        if not username:
            return False

        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return False

        if not user.is_active:
            return False

        return user

def generate_confirmation_key(user):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    return hashlib.sha1(user.username+salt).hexdigest()
