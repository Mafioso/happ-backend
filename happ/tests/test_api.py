from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from ..models import User
from ..factories import UserFactory


class CitiesTests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = reverse('cities-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        """
        Resourse is available with authentication only
        """
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
        """
        Resourse is not available without authentication
        """
        url = reverse('currencies-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        """
        Resourse is available with authentication only
        """
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


class AuthTests(APISimpleTestCase):

    def test_user_registration(self):
        """
        Registration resourse creates one user
        it creates embedded settings
        it returns JWT auth token
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'username': 'username',
            'email': 'email@mail.com',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='username')
        self.assertEqual(User.objects.count(), n+1)
        self.assertNotEqual(user.settings, None)
        self.assertNotEqual(response.data['token'], None)

    def test_user_registration_no_username(self):
        """
        Ensures that we cannot register without username
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'email': 'email@mail.com',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), n)

    def test_user_registration_no_email(self):
        """
        Ensures that we cannot register without email
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'username': 'username',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), n)

    def test_user_registration_no_password(self):
        """
        Ensures that we cannot register without password
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'username': 'username',
            'email': 'email@mail.com',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), n)
