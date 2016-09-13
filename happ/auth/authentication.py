from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _

from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class CookieJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "session_id"
    Cookie, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        session_id: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    def get_jwt_value(self, request):

        auth = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
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
