from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin

from .utils import get_jwt_value_from_cookies, check_payload, check_user


def get_user(request):
    if not hasattr(request, '_cached_user'):
        session_id = get_jwt_value_from_cookies(request.COOKIES)
        if not session_id:
            return None
        request._cached_user = check_user(check_payload(session_id))
    return request._cached_user

class UserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
