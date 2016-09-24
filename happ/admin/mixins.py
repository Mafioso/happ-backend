from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin

from happ.auth.utils import get_jwt_value_from_cookies, check_payload, check_user


class JWTAuthRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        session_id = get_jwt_value_from_cookies(self.request.COOKIES)
        if not session_id:
            return False
        payload = check_payload(session_id)
        return payload and check_user(payload)
