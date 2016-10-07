from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User, Interest
from happ.factories import (
    UserFactory,
    InterestFactory,
    CityFactory,
)
from happ.tests import *


class Tests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = prepare_url('admin-interests-list')
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

        url = prepare_url('admin-interests-list')
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

        url = prepare_url('admin-interests-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_interests(self):
        """
        We can search interests
        """
        Interest.objects.delete()
        for i in range(3):
            interest = InterestFactory(title='Hockey')
            interest.save()

        interest = InterestFactory(title='Beer')
        interest.save()

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

        url = prepare_url('admin-interests-list', query={'search': 'hoc'})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_create_interest(self):
        """
        we can create interest
        """
        n = Interest.objects.count()
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()

        url = prepare_url('admin-interests-list')

        interest_data = {
            'title': 'NewInterest name',
            'parent_id': None,
            'is_global': True,
            'local_cities': [],
            'color': '000000',
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
        response = self.client.post(url, data=interest_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ok for administrator
        u.role = User.ADMINISTRATOR
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=interest_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Interest.objects.count(), n+1)
        self.assertEqual(response.data['title'], 'NewInterest name')
        self.assertEqual(response.data['color'], '000000')

        # ok for root
        u.role = User.ROOT
        u.save()
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=interest_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Interest.objects.count(), n+2)
        self.assertEqual(response.data['title'], 'NewInterest name')
        self.assertEqual(response.data['color'], '000000')

    def test_update_interest(self):
        """
        we can update interest
        """
        cities = map(lambda x: str(CityFactory().id), range(3))
        interest = InterestFactory()
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

        url = prepare_url('admin-interests-detail', kwargs={'id': str(interest.id)})
        data = {
            'title': 'NewInterest name',
            'parent_id': None,
            'is_global': False,
            'local_cities': cities,
            'color': '00FF00',
        }
        n = Interest.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Interest.objects.count(), n)
        self.assertEqual(response.data['title'], 'NewInterest name')
        self.assertEqual(response.data['color'], '00FF00')

    def test_delete_interest(self):
        """
        we can delete interest
        """
        u = UserFactory(role=User.MODERATOR)
        u.set_password('123')
        u.save()

        i = InterestFactory()
        i.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('admin-interests-detail', kwargs={'id': str(i.id)})
        n = Interest.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Interest.objects.count(), n-1)

    def test_get_categories(self):
        """
        Ensure that we can get only categories with api
        """
        Interest.objects.delete()
        for i in range(3):
            interest = InterestFactory(parent=None)

        interest = InterestFactory(parent=interest)

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

        url = prepare_url('admin-interests-categories')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results'][2]['children']), 1)

    def test_get_children(self):
        """
        Ensure that we can get only children with api
        """
        Interest.objects.delete()
        for i in range(3):
            interest = InterestFactory(parent=None)

        interest = InterestFactory(parent=interest)

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

        url = prepare_url('admin-interests-children')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertNotEqual(response.data['results'][0]['parent'], None)
