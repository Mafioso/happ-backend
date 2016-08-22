from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from ..factories import UserFactory


class CitiesTests(APISimpleTestCase):

    def test_get_without_auth(self):
        url = reverse('cities-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        
        url = reverse('cities-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, response.data['token']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CurrenciesTests(APISimpleTestCase):

    def test_get_without_auth(self):
        url = reverse('currencies-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        
        url = reverse('currencies-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, response.data['token']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
