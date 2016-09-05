from datetime import datetime

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

    def test_edit_current_user(self):
        """
        We can get edit current user
        """
        u = UserFactory(**{
            'fullname': 'Michael Brown',
            'phone': '87015555555',
            'gender': 0,
            'date_of_birth': datetime(1991, 12, 23)
        })
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('users-current/edit')

        data = {
            'fullname': 'Adam Smith',
            'phone': '87017777777',
            'gender': 1,
            'date_of_birth': datetime(1990, 10, 15)
        }

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        u = User.objects.get(username=u.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(u.fullname, 'Adam Smith')
        self.assertEqual(u.phone, '87017777777')
        self.assertEqual(u.gender, 1)
        self.assertEqual(u.date_of_birth, datetime(1990, 10, 15))

    def test_set_language(self):
        """
        We can set language for current user
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

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('users-current/set/language')

        data = {
            'language': 'it',
        }
        response = self.client.post(url, data=data, format='json')
        u = User.objects.get(username=u.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['settings']['language'], 'it')
        self.assertEqual(u.settings.language, 'it')

    def test_set_language_no_lang(self):
        """
        We cannot set language for current user with no lang
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

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('users-current/set/language')

        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_language_wrong_lang(self):
        """
        We cannot set language for current user with wrong lang
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

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('users-current/set/language')

        data = {
            'language': 'kk',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
