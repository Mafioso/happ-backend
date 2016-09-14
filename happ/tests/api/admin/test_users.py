from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User
from happ.factories import (
    UserFactory,
)
from happ.tests import *


class Tests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = prepare_url('admin-users-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth_not_staff(self):
        """
        Resourse is not available for non-staff users
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

        url = prepare_url('admin-users-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_with_auth(self):
        """
        Resourse is available with authentication only and for staff
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('admin-users-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_staff_user(self):
        """
        we can create staff user
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        n = User.objects.count()

        url = prepare_url('admin-users-list')

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }

        ## lets create MODERATOR
        user_data = {
            'username': 'username1',
            'email': 'mail@mail.com',
            'password': '123',
            'role': User.MODERATOR
        }

        # restricted for moderator
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), n+1)
        self.assertEqual(response.data['username'], 'username1')

        user_data = {
            'username': 'username2',
            'email': 'mail@mail.com',
            'password': '123',
            'role': User.MODERATOR
        }

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), n+2)
        self.assertEqual(response.data['username'], 'username2')

        ## lets create ADMINISTRATOR
        user_data = {
            'username': 'username3',
            'email': 'mail@mail.com',
            'password': '123',
            'role': User.ADMINISTRATOR
        }

        # restricted for moderator
        u.role = User.MODERATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), n+3)
        self.assertEqual(response.data['username'], 'username3')

        ## lets create ROOT
        user_data = {
            'username': 'username3',
            'email': 'mail@mail.com',
            'password': '123',
            'role': User.ROOT
        }

        # restricted for moderator
        u.role = User.MODERATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user(self):
        """
        we can update user
        """
        user = UserFactory()
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        n = User.objects.count()

        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }

        user_data = {
            'username': 'username',
            'email': 'mail@mail.com',
        }

        # restricted for moderator
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), n)
        self.assertEqual(response.data['username'], 'username')

        # ok for root
        user_data = {
            'username': 'username2',
            'email': 'mail@mail.com',
        }
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), n)
        self.assertEqual(response.data['username'], 'username2')

        ## trying to change role to MODERATOR
        user_data = {
            'role': User.MODERATOR,
        }

        # restricted to MODERATOR
        u.role = User.MODERATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), n)
        self.assertEqual(response.data['role'], User.MODERATOR)

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), n)
        self.assertEqual(response.data['role'], User.MODERATOR)

        ## trying to change role to ADMINISTRATOR
        user_data = {
            'role': User.ADMINISTRATOR,
        }

        # restricted to MODERATOR
        u.role = User.MODERATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), n)
        self.assertEqual(response.data['role'], User.ADMINISTRATOR)

        ## trying to change role to ROOT
        user_data = {
            'role': User.ROOT,
        }

        # restricted to MODERATOR
        u.role = User.MODERATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
