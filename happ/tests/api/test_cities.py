from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User, City
from happ.factories import (
    UserFactory,
    CountryFactory,
    CityFactory,
)
from .. import *


class Tests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = prepare_url('cities-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        """
        Resourse is available with authentication only
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

        url = prepare_url('cities-list')
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

        url = prepare_url('cities-list', query={'search': 'petro'})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_create_city(self):
        """
        we can create city
        """
        n = City.objects.count()
        country = CountryFactory()
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

        url = prepare_url('cities-list')
        data = {
            'name': 'NewCity name',
            'country_id': str(country.id),
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), n+1)
        self.assertEqual(response.data['country_name'], country.name)

    def test_user_set_city(self):
        """
        We can set city for user
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
        self.assertEqual(u.settings.city, None)

        city = CityFactory()
        city.save()

        url = prepare_url('cities-set', kwargs={'id': str(city.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        u = User.objects.get(id=u.id)
        self.assertEqual(u.settings.city, city)
