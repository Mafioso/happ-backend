from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User, LogEntry
from happ.factories import (
    UserFactory,
    CityFactory,
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

    def test_get_users_list(self):
        """
        it returns only REGULAR and ORGANIZER users
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

        u = UserFactory(role=User.REGULAR)
        u = UserFactory(role=User.ORGANIZER)

        url = prepare_url('admin-users-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_users_organizers(self):
        """
        it returns only ORGANIZER users
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

        u = UserFactory(role=User.REGULAR)
        u = UserFactory(role=User.ORGANIZER)

        url = prepare_url('admin-users-organizers')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_staff_user(self):
        """
        we can create staff user
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        n = User.objects.count()
        log_n = LogEntry.objects.count()

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
        self.assertEqual(LogEntry.objects.count(), log_n+1)

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
        self.assertEqual(LogEntry.objects.count(), log_n+2)

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
        self.assertEqual(LogEntry.objects.count(), log_n+3)

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
        log_n = LogEntry.objects.count()

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
        self.assertEqual(LogEntry.objects.count(), log_n+1)

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
        self.assertEqual(LogEntry.objects.count(), log_n+2)

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
        self.assertEqual(LogEntry.objects.count(), log_n+3)

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
        self.assertEqual(LogEntry.objects.count(), log_n+4)

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
        self.assertEqual(LogEntry.objects.count(), log_n+5)

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

    def test_delete_user(self):
        """
        we can delete user
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        log_n = LogEntry.objects.count()

        user = UserFactory()
        n = User.objects.count()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }

        ## regular user

        # ok for moderator
        user = UserFactory()
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        user = UserFactory()
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+2)

        # ok for root
        u.role = User.ROOT
        u.save()
        user = UserFactory()
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+3)

        ## moderator user

        # restricted for moderator
        u.role = User.MODERATOR
        u.save()
        user = UserFactory(role=User.MODERATOR)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        user = UserFactory(role=User.MODERATOR)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+4)

        # ok for root
        u.role = User.ROOT
        u.save()
        user = UserFactory(role=User.MODERATOR)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+5)

        ## administrator user

        # restricted for moderator
        u.role = User.MODERATOR
        u.save()
        user = UserFactory(role=User.ADMINISTRATOR)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        user = UserFactory(role=User.ADMINISTRATOR)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for root
        u.role = User.ROOT
        u.save()
        user = UserFactory(role=User.ADMINISTRATOR)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+6)

        ## root user

        # restricted for moderator
        user = UserFactory(role=User.ROOT)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        user = UserFactory(role=User.ROOT)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # restricted for root
        u.role = User.ROOT
        u.save()
        user = UserFactory(role=User.ROOT)
        n = User.objects.count()
        url = prepare_url('admin-users-detail', kwargs={'id': str(user.id)})
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_activate(self):
        """
        we can activate user through API
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        log_n = LogEntry.objects.count()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        u = UserFactory(role=User.REGULAR)

        url = prepare_url('admin-users-activate', kwargs={'id': str(u.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        u = User.objects.get(id=u.id)
        self.assertTrue(u.is_active)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

    def test_deactivate(self):
        """
        we can deactivate user through API
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        log_n = LogEntry.objects.count()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        u = UserFactory(role=User.REGULAR)

        url = prepare_url('admin-users-deactivate', kwargs={'id': str(u.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        u = User.objects.get(id=u.id)
        self.assertFalse(u.is_active)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

    def test_assign_city(self):
        """
        we can assign city for moderator through API
        """

        u1 = UserFactory(role=User.MODERATOR)

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
        url = prepare_url('admin-users-assign-city', kwargs={'id': str(u1.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        c = CityFactory()
        data = {
            'city_id': str(c.id)
        }

        # restricted for moderator
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        u1 = User.objects.get(id=u1.id)
        self.assertEqual(u1.assigned_city, c)

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        u1 = User.objects.get(id=u1.id)
        self.assertEqual(u1.assigned_city, c)

    def test_assign_city_for_non_staff(self):
        """
        we cannot assign city for regular and organizer users through API
        """
        c = CityFactory()
        u = UserFactory(role=User.ADMINISTRATOR)
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        u = UserFactory(role=User.ORGANIZER)
        data = {
            'city_id': str(c.id)
        }

        url = prepare_url('admin-users-assign-city', kwargs={'id': str(u.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        u = UserFactory(role=User.REGULAR)
        data = {
            'city_id': str(c.id)
        }

        url = prepare_url('admin-users-assign-city', kwargs={'id': str(u.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
