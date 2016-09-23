from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .utils import get_jwt_value_from_cookies


class CookieJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "session_id"
    Cookie, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        session_id: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    def get_jwt_value(self, request):
        return get_jwt_value_from_cookies(request.COOKIES)
