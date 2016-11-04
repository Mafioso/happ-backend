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
        url = prepare_url('interests-list')
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

        url = prepare_url('interests-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_only_activated_interests(self):
        """
        it returns only those interests that are marked as is_active
        """
        for i in range(3):
            InterestFactory(parent=None)

        InterestFactory(parent=None, is_active=False)

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

        url = prepare_url('interests-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)


    def test_search_interests(self):
        """
        We can search interests
        """
        Interest.objects.delete()
        for i in range(3):
            interest = InterestFactory(title='Hockey', parent=None)
            interest.save()

        interest = InterestFactory(title='Beer', parent=None)
        interest.save()

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

        url = prepare_url('interests-list', query={'search': 'hoc'})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_user_set_interests(self):
        """
        We can assign list of interests to user
        """
        u = UserFactory(interests=[])
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.assertEqual(len(u.interests), 0)

        interests = []
        for i in range(3):
            interest = InterestFactory()
            interest.save()
            interests.append(interest)

        url = prepare_url('interests-set')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=map(lambda x: str(x.id), interests), format='json')
        # user has no city, so he cannot set interests
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        u.settings.city = CityFactory()
        u.save()

        response = self.client.post(url, data=map(lambda x: str(x.id), interests), format='json')
        u = User.objects.get(id=u.id)
        self.assertEqual(len(u.interests), 1)
        self.assertEqual(len(u.current_interests), 3)

        # lets change the list of interests for current city
        # the amount of CityInterests records should not have been changed
        interests = []
        for i in range(4):
            interest = InterestFactory()
            interest.save()
            interests.append(interest)

        response = self.client.post(url, data=map(lambda x: str(x.id), interests), format='json')
        u = User.objects.get(id=u.id)
        self.assertEqual(len(u.interests), 1)
        self.assertEqual(len(u.current_interests), 4)

        # lets change user's current city and save interests for this city
        # the amount of CityInterests should have been incremented
        u.settings.city = CityFactory()
        u.save()

        interests = []
        for i in range(2):
            interest = InterestFactory()
            interest.save()
            interests.append(interest)

        response = self.client.post(url, data=map(lambda x: str(x.id), interests), format='json')
        u = User.objects.get(id=u.id)
        self.assertEqual(len(u.interests), 2)
        self.assertEqual(len(u.current_interests), 2)
