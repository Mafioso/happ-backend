import random
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
    CityInterestsFactory,
)
from happ.serializers import EventSerializer
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

        # full
        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
            'max_price': 120,
            'image_ids': [],
            'geopoint': {'lng': 1, 'lat':0},
            'interest_ids': map(lambda _: str(InterestFactory().id), range(3)),
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(n+1, Event.objects.count())
        e = Event.objects.get(id=response.data['id'])
        self.assertEqual(e.title, 'New event')
        self.assertEqual(e.min_price, 100)
        self.assertEqual(e.max_price, 120)
        self.assertEqual(e.geopoint['coordinates'], [1, 0])
        self.assertEqual(len(e.interests), 3)

        es = EventSerializer(e).data
        self.assertEqual(es['geopoint'], {'lng': 1, 'lat':0})

        n = Event.objects.count()

        # no max_price
        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'min_price': 100,
            'image_ids': [],
            'geopoint': {'lng': 1, 'lat':0},
            'interest_ids': [],
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(n+1, Event.objects.count())
        e = Event.objects.get(id=response.data['id'])
        self.assertEqual(e.title, 'New event')
        self.assertEqual(e.min_price, 100)
        self.assertEqual(e.max_price, None)
        self.assertEqual(e.geopoint['coordinates'], [1, 0])
        self.assertEqual(len(e.interests), 0)

        es = EventSerializer(e).data
        self.assertEqual(es['geopoint'], {'lng': 1, 'lat':0})

        n = Event.objects.count()

        # no min_price
        data = {
            'title': 'New event',
            'city_id': str(CityFactory.create().id),
            'currency_id': str(CurrencyFactory.create().id),
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(days=1, hours=1),
            'max_price': 120,
            'image_ids': [],
            'geopoint': {'lng': 1, 'lat':0},
            'interest_ids': [],
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(n+1, Event.objects.count())
        e = Event.objects.get(id=response.data['id'])
        self.assertEqual(e.title, 'New event')
        self.assertEqual(e.min_price, None)
        self.assertEqual(e.max_price, 120)
        self.assertEqual(e.geopoint['coordinates'], [1, 0])
        self.assertEqual(len(e.interests), 0)

        es = EventSerializer(e).data
        self.assertEqual(es['geopoint'], {'lng': 1, 'lat':0})

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
            'image_ids': [],
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
            'image_ids': [],
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
            'image_ids': [],
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
            'image_ids': [],
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
            'image_ids': [],
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
            'image_ids': [],
            'interest_ids': [],
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
            'image_ids': [],
            'interest_ids': [],
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

        e = EventFactory(status=random.choice(Event.STATUSES))
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
            'geopoint': {'lng': 1, 'lat':0},
            'image_ids': [],
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New event')
        self.assertEqual(response.data['status'], Event.MODERATION)
        self.assertEqual(response.data['min_price'], 100)
        self.assertEqual(response.data['max_price'], 120)
        self.assertEqual(response.data['geopoint'], {'lng': 1, 'lat':0})
        self.assertEqual(Event.objects.count(), n)

    def test_edit_event_another_author(self):
        """
        we cannot edit event of other users
        """
        ou = UserFactory()
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory(status=random.choice(Event.STATUSES), author=ou)
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
            'geopoint': {'lng': 1, 'lat':0},
            'image_ids': [],
        }
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        e2 = Event.objects.get(id=e.id)
        self.assertEqual(e2.title, e.title)
        self.assertEqual(e2.status, e2.status)
        self.assertEqual(e2.min_price, e2.min_price)
        self.assertEqual(e2.max_price, e2.max_price)
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

    def test_delete_event_another_author(self):
        """
        we cannot delete event of other users
        """
        ou = UserFactory()
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory(author=ou)
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), n)

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
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.count(), (n+1))
        self.assertNotEqual(response.data['id'], str(e.id))

    def test_copy_event_another_author(self):
        """
        we cannot copy event of other users
        """
        ou = UserFactory()
        u = UserFactory()
        u.set_password('123')
        u.save()

        e = EventFactory(author=ou)
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
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), n)

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
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # we cannot upvote it again
        response = self.client.post(url, format='json')
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
        response = self.client.post(url, format='json')
        # we cannot downvote before upvote
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        e.upvote(u)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

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
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # we cannot add it to favourites again
        response = self.client.post(url, format='json')
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
        response = self.client.post(url, format='json')
        # we cannot remove from favourites before adding
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        e.add_to_favourites(u)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_favourite_events(self):
        """
        we can get favourite event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        for i in range(5):
            EventFactory()
        map(lambda x: x.add_to_favourites(u), Event.objects.all()[:4])

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-favourites')

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)

    def test_get_events_feed(self):
        """
        we can get events feed
        we can get sorted by popularity feed
        we can filter feed
        """
        c1 = CityFactory()
        ins_set = map(lambda _: InterestFactory(), range(3))
        ci1 = CityInterestsFactory(c=c1, ins=ins_set)

        # correct
        for i in range(5):
            EventFactory(
                title='t{}'.format(i),
                description='t{}_description'.format(i),
                votes_num=(5-i),
                start_date='20160520',
                start_time='0{}3000'.format(i),
                min_price=i,
                max_price=i+10,
                city=c1,
                interests=[random.choice(ins_set)],
                is_active=True,
                status=Event.APPROVED,
            )

        # inactive
        for i in range(4):
            EventFactory(
                title='t{}'.format(i),
                description='t{}_description'.format(i),
                votes_num=(5-i),
                start_date='20160520',
                start_time='0{}3000'.format(i),
                min_price=i,
                max_price=i+10,
                city=c1,
                interests=[random.choice(ins_set)],
                is_active=False,
                status=Event.APPROVED,
            )

        # not APPROVED
        for i in range(3):
            EventFactory(
                title='t{}'.format(i),
                description='dt{}'.format(i),
                votes_num=(5-i),
                start_date='20170520',
                start_time='0{}3000'.format(i),
                min_price=i,
                max_price=i+10,
                city=c1,
                interests=[random.choice(ins_set)],
                is_active=True,
                status=random.choice([Event.MODERATION, Event.REJECTED]),
            )

        u = UserFactory()
        u.interests = [ci1]
        u.settings.city = c1
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-feed')

        ## simple
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(response.data['results'][0]['title'], 't0')
        self.assertEqual(response.data['results'][1]['title'], 't1')
        self.assertEqual(response.data['results'][2]['title'], 't2')
        self.assertEqual(response.data['results'][3]['title'], 't3')
        self.assertEqual(response.data['results'][4]['title'], 't4')

        ## ordering
        url = prepare_url('events-feed', query={'order': 'popular'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(response.data['results'][0]['title'], 't0')
        self.assertEqual(response.data['results'][1]['title'], 't1')
        self.assertEqual(response.data['results'][2]['title'], 't2')
        self.assertEqual(response.data['results'][3]['title'], 't3')
        self.assertEqual(response.data['results'][4]['title'], 't4')

        ## filtering
        # start_time
        url = prepare_url('events-feed', query={'start_time': '033000'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['title'], 't3')
        self.assertEqual(response.data['results'][1]['title'], 't4')
        # min_price
        url = prepare_url('events-feed', query={'min_price': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(response.data['results'][0]['title'], 't1')
        self.assertEqual(response.data['results'][1]['title'], 't2')
        self.assertEqual(response.data['results'][2]['title'], 't3')
        self.assertEqual(response.data['results'][3]['title'], 't4')
        # max_price
        url = prepare_url('events-feed', query={'max_price': 11})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['title'], 't0')
        self.assertEqual(response.data['results'][1]['title'], 't1')
        # min_price and max_price
        url = prepare_url('events-feed', query={'min_price': 1, 'max_price': 11})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 't1')

        ## searching
        # title
        url = prepare_url('events-feed', query={'search': 't1'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 't1')
        # description
        url = prepare_url('events-feed', query={'search': 't1_d'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 't1')

    def test_get_events_featured(self):
        """
        we can get featured events
        """
        c1 = CityFactory()
        ins_set = map(lambda _: InterestFactory(), range(3))
        ci1 = CityInterestsFactory(c=c1, ins=ins_set)

        # correct
        for i in range(5):
            EventFactory(
                city=c1,
                interests=[random.choice(ins_set)],
                type=Event.FEATURED,
                status=Event.APPROVED,
                is_active=True
            )

        # inactive
        for i in range(5):
            EventFactory(
                city=c1,
                interests=[random.choice(ins_set)],
                type=Event.FEATURED,
                status=Event.APPROVED,
                is_active=False
            )

        # not APPROVED
        for i in range(3):
            EventFactory(
                city=c1,
                interests=[random.choice(ins_set)],
                type=Event.FEATURED,
                status=random.choice([Event.MODERATION, Event.REJECTED]),
                is_active=True
            )

        u = UserFactory()
        u.interests = [ci1]
        u.settings.city = c1
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-featured')

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_get_events_organizer(self):
        """
        we can get organizer events
        """

        u1 = UserFactory()
        u1.set_password('123')
        u1.save()

        u2 = UserFactory()

        for i in range(5):
            EventFactory(author=u1)

        for i in range(3):
            EventFactory(author=u2)

        auth_url = prepare_url('login')
        data = {
            'username': u1.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-organizer')

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_get_events_explore(self):
        """
        we can get explore events
        """

        c = CityFactory()

        parent_interest1 = InterestFactory(parent=None)
        parent_interest2 = InterestFactory(parent=None)

        # this set is not used
        ins_set1 = map(lambda _: InterestFactory(parent=parent_interest1), range(5))

        # this set is assigned to user for current city
        ins_set2 = map(lambda _: InterestFactory(parent=parent_interest2), range(3))

        ci = CityInterestsFactory(c=c, ins=[parent_interest1])

        # correct
        for i in range(3):
            EventFactory(city=c, interests=[random.choice(ins_set1)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED, is_active=True)

        # inactive
        for i in range(3):
            EventFactory(city=c, interests=[random.choice(ins_set1)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED, is_active=False)

        # not APPROVED
        for i in range(3):
            EventFactory(city=c, interests=[random.choice(ins_set1)], type=random.choice([Event.NORMAL, Event.ADS]), status=random.choice([Event.MODERATION, Event.REJECTED]), is_active=True)

        # other interest set
        for i in range(4):
            EventFactory(city=c, interests=[random.choice(ins_set2)], type=random.choice([Event.NORMAL, Event.ADS]), status=Event.APPROVED, is_active=True)

        u = UserFactory()
        u.interests = [ci]
        u.settings.city = c
        u.set_password('123')
        u.save()

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = prepare_url('events-explore')

        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_events_map(self):
        """
        we can get events for map view
        """
        c = CityFactory()
        ins_set = map(lambda _: InterestFactory(), range(3))
        ci = CityInterestsFactory(c=c, ins=ins_set)

        u = UserFactory()
        u.interests = [ci]
        u.settings.city = c
        u.set_password('123')
        u.save()

        center = [random.uniform(-180, 180), random.uniform(-90, 90)]
        radius = 500

        # correct
        for i in range(5):
            EventFactory(city=c,
                         interests=[random.choice(ins_set)],
                         type=Event.NORMAL,
                         status=Event.APPROVED,
                         is_active=True,
                         geopoint=generate_geopoint(center, radius)
            )

        # inactive
        for i in range(5):
            EventFactory(city=c,
                         interests=[random.choice(ins_set)],
                         type=Event.NORMAL,
                         status=Event.APPROVED,
                         is_active=False,
                         geopoint=generate_geopoint(center, radius)
            )

        # not APPROVED
        for i in range(5):
            EventFactory(city=c,
                         interests=[random.choice(ins_set)],
                         type=Event.NORMAL,
                         status=random.choice([Event.MODERATION, Event.REJECTED]),
                         is_active=True,
                         geopoint=generate_geopoint(center, radius)
            )

        # rejected by geoposition
        for i in range(10):
            EventFactory(city=c,
                         interests=[random.choice(ins_set)],
                         type=Event.NORMAL,
                         status=Event.APPROVED,
                         is_active=True,
                         geopoint=generate_geopoint(center, radius, inside=False)
            )

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('events-map')

        data = {
            'radius': radius,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        data = {
            'center': center,
            'radius': radius,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_complaint_event(self):
        """
        we can send a complaint to event
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
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('events-complaint', kwargs={'id': str(e.id)})
        data = {
            'text': 'WTF?'
        }

        self.assertEqual(len(e.complaints), 0)
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(e.complaints), 1)
        self.assertEqual(e.complaints[0].text, 'WTF?')
        self.assertEqual(e.complaints[0].author.id, u.id)

    def test_activate(self):
        """
        we can activate event through API
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

        i = EventFactory(is_active=False)

        url = prepare_url('events-activate', kwargs={'id': str(i.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        i = Event.objects.get(id=i.id)
        self.assertTrue(i.is_active)

    def test_activate_another_author(self):
        """
        we cannot activate event through API of other users
        """
        ou = UserFactory()
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

        i = EventFactory(is_active=False, author=ou)

        url = prepare_url('events-activate', kwargs={'id': str(i.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        i = Event.objects.get(id=i.id)
        self.assertFalse(i.is_active)

    def test_deactivate(self):
        """
        we can deactivate event through API
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

        i = EventFactory(is_active=True)

        url = prepare_url('events-deactivate', kwargs={'id': str(i.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        i = Event.objects.get(id=i.id)
        self.assertFalse(i.is_active)

    def test_deactivate_another_author(self):
        """
        we cannot deactivate event through API of other users
        """
        ou = UserFactory()
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

        i = EventFactory(is_active=True, author=ou)

        url = prepare_url('events-deactivate', kwargs={'id': str(i.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        i = Event.objects.get(id=i.id)
        self.assertTrue(i.is_active)
