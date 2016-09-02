from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User, Currency
from happ.factories import UserFactory
from .. import *


class UsersTests(APISimpleTestCase):
    def test_get_current_user(self):
        """
        We can get current user
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('users-current')

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], u.username)
