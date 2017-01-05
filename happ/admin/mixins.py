from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin

from happ.models import User, StaticText
from happ.auth.utils import get_jwt_value_from_cookies, check_payload, check_user


class JWTAuthRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        session_id = get_jwt_value_from_cookies(self.request.COOKIES)
        if not session_id:
            return False
        payload = check_payload(session_id)
        return payload and check_user(payload)


class RoleMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RoleMixin, self).get_context_data(**kwargs)
        context['roles'] = User.get_roles_dict()
        return context


class StaticTextMixin(object):
    def get_context_data(self, **kwargs):
        context = super(StaticTextMixin, self).get_context_data(**kwargs)
        try:
            st = StaticText.objects.get(type=self.type)
        except:
            st = StaticText(type=self.type)
        context['text'] = st.text
        return context
