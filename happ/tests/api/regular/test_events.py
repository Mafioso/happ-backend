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
from happ.tests import *


class Tests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = prepare_url('events-list')
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

        url = prepare_url('events-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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
            'images': [],
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

    def test_edit_event(self):
        """
        we can edit event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-detail', kwargs={'id': str(e.id)})
        n = Event.objects.count()

        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1),
            'min_price': 100,
            'max_price': 120,
            'images': [],
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New event')
        self.assertEqual(response.data['min_price'], 100)
        self.assertEqual(response.data['max_price'], 120)
        self.assertEqual(Event.objects.count(), n)

    def test_delete_event(self):
        """
        we can delete event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-detail', kwargs={'id': str(e.id)})
        n = Event.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), n-1)

    def test_copy_event(self):
        """
        we can copy event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-copy', kwargs={'id': str(e.id)})
        n = Event.objects.count()

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.count(), (n+1))
        self.assertNotEqual(response.data['id'], str(e.id))

    def test_upvote_event(self):
        """
        we can upvote event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-upvote', kwargs={'id': str(e.id)})

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # we cannot upvote it again
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_downvote_event(self):
        """
        we can downvote event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-downvote', kwargs={'id': str(e.id)})

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        # we cannot downvote before upvote
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        e.upvote(u)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fav_event(self):
        """
        we can fav event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-fav', kwargs={'id': str(e.id)})

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # we cannot add it to favourites again
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfav_event(self):
        """
        we can unfav event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory()
        e.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-unfav', kwargs={'id': str(e.id)})

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        # we cannot remove from favourites before adding
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        e.add_to_favourites(u)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
