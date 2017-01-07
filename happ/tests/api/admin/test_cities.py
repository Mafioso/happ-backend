from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User, City, LogEntry
from happ.factories import (
    UserFactory,
    CountryFactory,
    CityFactory,
)
from happ.tests import *


class Tests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = prepare_url('admin-cities-list')
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

        url = prepare_url('admin-cities-list')
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

        url = prepare_url('admin-cities-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_cities(self):
        """
        We can search cities
        """
        City.objects.delete()
        for i in range(3):
            city = CityFactory(name='Petropavlovsk')
            city.save()

        city = CityFactory(name='Almaty')
        city.save()

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

        url = prepare_url('admin-cities-list', query={'search': 'petro'})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_create_city(self):
        """
        we can create city
        """
        n = City.objects.count()
        log_n = LogEntry.objects.count()
        country = CountryFactory()
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()

        url = prepare_url('admin-cities-list')

        city_data = {
            'name': 'NewCity name',
            'country_id': str(country.id),
        }

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }

        # restricted for moderator
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(City.objects.count(), n)
        self.assertEqual(LogEntry.objects.count(), log_n)

        # restricted for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(City.objects.count(), n)
        self.assertEqual(LogEntry.objects.count(), log_n)

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=city_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), n+1)
        self.assertEqual(response.data['country_name'], country.name)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

    def test_update_city(self):
        """
        we can update city
        """
        country = CountryFactory()
        city = CityFactory()
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

        url = prepare_url('admin-cities-detail', kwargs={'id': str(city.id)})
        data = {
            'name': 'NewCity name',
            'country_id': str(country.id),
            'is_active': False
        }
        n = City.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(City.objects.count(), n)
        self.assertEqual(response.data['name'], 'NewCity name')
        self.assertEqual(response.data['is_active'], False)
        self.assertEqual(response.data['country_name'], country.name)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

    def test_delete_city(self):
        """
        we can delete city
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()
        log_n = LogEntry.objects.count()

        c = CityFactory()
        c.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('admin-cities-detail', kwargs={'id': str(c.id)})
        n = City.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(City.objects.count(), n-1)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

    def test_activate(self):
        """
        we can activate city through API
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

        c = CityFactory(is_active=False)

        url = prepare_url('admin-cities-activate', kwargs={'id': str(c.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        c = City.objects.get(id=c.id)
        self.assertTrue(c.is_active)
        self.assertEqual(LogEntry.objects.count(), log_n+1)

    def test_deactivate(self):
        """
        we can deactivate city through API
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

        c = CityFactory(is_active=True)

        url = prepare_url('admin-cities-deactivate', kwargs={'id': str(c.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        c = City.objects.get(id=c.id)
        self.assertFalse(c.is_active)
        self.assertEqual(LogEntry.objects.count(), log_n+1)
