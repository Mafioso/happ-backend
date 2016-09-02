from datetime import datetime, timedelta

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User, City, Currency, Event
from happ.factories import (
    UserFactory,
    CityFactory,
    CurrencyFactory,
    EventFactory,
    LocalizedFactory,
    InterestFactory,
)
from .. import *


class EventTests(APISimpleTestCase):
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

        url = prepare_url('interests-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, response.data['token']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event(self):
        """
        We can create event
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(n+1, Event.objects.count())

        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(n+1, Event.objects.count())

        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(n+1, Event.objects.count())


    def test_create_event_no_title(self):
        """
        We cannot create event without title
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(n, Event.objects.count())

    def test_create_event_no_city_id(self):
        """
        We cannot create event without city_id
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(n, Event.objects.count())

    def test_create_event_no_currency_id(self):
        """
        We cannot create event without currency_id
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(n, Event.objects.count())

    def test_create_event_no_price(self):
        """
        We cannot create event without price
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(n, Event.objects.count())

    def test_create_event_min_max(self):
        """
        We cannot create event if min_price is greater than max_price
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 120,
            'max_price': 100,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(n, Event.objects.count())

    def test_create_event_start_end_date(self):
        """
        We cannot create event if start date is later than end date
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

        url = prepare_url('events-list')
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now() + timedelta(days=1),
            'end_datetime': datetime.now(),
            'min_price': 100,
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(n, Event.objects.count())

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now() + timedelta(hours=1),
            'end_datetime': datetime.now(),
            'min_price': 100,
            'max_price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(n, Event.objects.count())

    def test_retrieve_event(self):
        """
        We can retrieve event
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

        e = EventFactory()
        e.save()
        url = prepare_url('events-detail', kwargs={'id': str(e.id)})

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], e.title)

    def test_retrieve_event_localized(self):
        """
        We can retrieve event with translated field according to current user's language
        """
        language = 'de'
        localized_title = 'german title'
        u = UserFactory()
        u.set_password('123')
        u.settings.language = language
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        e = EventFactory()
        e.save()
        l = LocalizedFactory(entity=e, language=language, data={'title': localized_title})
        l.save()
        url = prepare_url('events-detail', kwargs={'id': str(e.id)})

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], localized_title)

    def test_user_set_interests(self):
        """
        We can set list of interests for user
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        u = User.objects.get(id=u.id)
        self.assertEqual(len(u.interests), 3)
