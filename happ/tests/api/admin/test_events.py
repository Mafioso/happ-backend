import random
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.utils import date_to_string
from happ.models import User, City, Currency, Event
from happ.factories import (
    UserFactory,
    CityFactory,
    CurrencyFactory,
    EventFactory,
    EventTimeFactory,
    LocalizedFactory,
    InterestFactory,
    CityInterestsFactory,
)
from happ.tests import *


class Tests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = prepare_url('admin-events-list')
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

        url = prepare_url('admin-events-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_with_auth(self):
        """
        Resourse is available with authentication only
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

        url = prepare_url('admin-events-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_event_list(self):
        """
        we can use filter event list
        """
        c1 = CityFactory()
        c2 = CityFactory()
        c3 = CityFactory()
        i1 = InterestFactory()
        i2 = InterestFactory()
        i3 = InterestFactory()

        for i in range(5):
            e = EventFactory(
                title='t1{}'.format(i),
                description='t1{}_description'.format(i),
                votes_num=(5-i),
                min_price=i,
                max_price=i+10,
                city=c1,
                interests=[i2, i3],
                is_active=True,
                status=Event.APPROVED,
                datetimes=[EventTimeFactory(
                    date=(datetime.now()+timedelta(days=i)).date(),
                    start_time='0{}3000'.format(i),
                    end_time='0{}3000'.format(i+1),
                )]
            )

        for i in range(4):
            e = EventFactory(
                title='t2{}'.format(i),
                description='t2{}_description'.format(i),
                votes_num=(5-i),
                min_price=i,
                max_price=i+10,
                city=c2,
                interests=[i1, i2],
                is_active=True,
                status=Event.APPROVED,
                datetimes=[EventTimeFactory(
                    date=(datetime.now()+timedelta(days=i)).date(),
                    start_time='1{}3000'.format(i),
                    end_time='1{}3000'.format(i+1),
                )]
            )

        for i in range(3):
            e = EventFactory(
                title='t3{}'.format(i),
                description='t3{}_description'.format(i),
                votes_num=(5-i),
                min_price=i,
                max_price=i+10,
                city=c3,
                interests=[i1, i3],
                is_active=True,
                status=Event.APPROVED,
                datetimes=[EventTimeFactory(
                    date=(datetime.now()+timedelta(days=i)).date(),
                    start_time='2{}3000'.format(i),
                    end_time='2{}3000'.format(i+1),
                )]
            )

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
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('admin-events-list')

        # start_time
        url = prepare_url('admin-events-list', query={'start_time': '033000'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['results'][0]['title'], 't32')
        self.assertEqual(response.data['results'][1]['title'], 't31')
        # end_time
        url = prepare_url('admin-events-list', query={'end_time': '033000'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], 't12')
        self.assertEqual(response.data['results'][1]['title'], 't11')
        self.assertEqual(response.data['results'][2]['title'], 't10')
        # start_time and end_time
        url = prepare_url('admin-events-list', query={'start_time': '033000', 'end_time': '043000'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 't13')
        # start_date
        url = prepare_url('admin-events-list', query={'start_date': date_to_string((datetime.now()+timedelta(days=3)).date(), settings.DATE_STRING_FIELD_FORMAT)})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], 't23')
        self.assertEqual(response.data['results'][1]['title'], 't14')
        self.assertEqual(response.data['results'][2]['title'], 't13')
        # end_date
        url = prepare_url('admin-events-list', query={'end_date': date_to_string((datetime.now()+timedelta(days=3)).date(), settings.DATE_STRING_FIELD_FORMAT)})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 11)
        self.assertEqual(response.data['results'][0]['title'], 't32')
        self.assertEqual(response.data['results'][1]['title'], 't31')
        self.assertEqual(response.data['results'][2]['title'], 't30')
        self.assertEqual(response.data['results'][3]['title'], 't23')
        self.assertEqual(response.data['results'][4]['title'], 't22')
        self.assertEqual(response.data['results'][5]['title'], 't21')
        self.assertEqual(response.data['results'][6]['title'], 't20')
        self.assertEqual(response.data['results'][7]['title'], 't13')
        self.assertEqual(response.data['results'][8]['title'], 't12')
        self.assertEqual(response.data['results'][9]['title'], 't11')
        # start_date and end_date
        url = prepare_url('admin-events-list', query={'start_date': date_to_string((datetime.now()+timedelta(days=3)).date(), settings.DATE_STRING_FIELD_FORMAT), 'end_date': date_to_string((datetime.now()+timedelta(days=4)).date(), settings.DATE_STRING_FIELD_FORMAT)})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], 't23')
        self.assertEqual(response.data['results'][1]['title'], 't14')
        self.assertEqual(response.data['results'][2]['title'], 't13')

        # min_price
        url = prepare_url('admin-events-list', query={'min_price': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['results'][0]['title'], 't32')
        self.assertEqual(response.data['results'][1]['title'], 't31')
        self.assertEqual(response.data['results'][2]['title'], 't23')
        self.assertEqual(response.data['results'][3]['title'], 't22')
        self.assertEqual(response.data['results'][4]['title'], 't21')
        self.assertEqual(response.data['results'][5]['title'], 't14')
        self.assertEqual(response.data['results'][6]['title'], 't13')
        self.assertEqual(response.data['results'][7]['title'], 't12')
        self.assertEqual(response.data['results'][8]['title'], 't11')
        # max_price
        url = prepare_url('admin-events-list', query={'max_price': 11})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertEqual(response.data['results'][0]['title'], 't31')
        self.assertEqual(response.data['results'][1]['title'], 't30')
        self.assertEqual(response.data['results'][2]['title'], 't21')
        self.assertEqual(response.data['results'][3]['title'], 't20')
        self.assertEqual(response.data['results'][4]['title'], 't11')
        self.assertEqual(response.data['results'][5]['title'], 't10')
        # min_price and max_price
        url = prepare_url('admin-events-list', query={'min_price': 1, 'max_price': 11})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], 't31')
        self.assertEqual(response.data['results'][1]['title'], 't21')
        self.assertEqual(response.data['results'][2]['title'], 't11')

        # city (one city)
        url = prepare_url('admin-events-list', query={'city': c1.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(response.data['results'][0]['title'], 't14')
        self.assertEqual(response.data['results'][1]['title'], 't13')
        self.assertEqual(response.data['results'][2]['title'], 't12')
        self.assertEqual(response.data['results'][3]['title'], 't11')
        self.assertEqual(response.data['results'][4]['title'], 't10')
        # several cities
        url = prepare_url('admin-events-list', query={'city': [c1.id, c2.id]})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['results'][0]['title'], 't23')
        self.assertEqual(response.data['results'][1]['title'], 't22')
        self.assertEqual(response.data['results'][2]['title'], 't21')
        self.assertEqual(response.data['results'][3]['title'], 't20')
        self.assertEqual(response.data['results'][4]['title'], 't14')
        self.assertEqual(response.data['results'][5]['title'], 't13')
        self.assertEqual(response.data['results'][6]['title'], 't12')
        self.assertEqual(response.data['results'][7]['title'], 't11')
        self.assertEqual(response.data['results'][8]['title'], 't10')

        # interests (one interest)
        url = prepare_url('admin-events-list', query={'interests': i1.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)
        self.assertEqual(response.data['results'][0]['title'], 't32')
        self.assertEqual(response.data['results'][1]['title'], 't31')
        self.assertEqual(response.data['results'][2]['title'], 't30')
        self.assertEqual(response.data['results'][3]['title'], 't23')
        self.assertEqual(response.data['results'][4]['title'], 't22')
        self.assertEqual(response.data['results'][5]['title'], 't21')
        self.assertEqual(response.data['results'][6]['title'], 't20')
        # several interests
        url = prepare_url('admin-events-list', query={'interests': [i1.id, i2.id]})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 12)
        self.assertEqual(response.data['results'][0]['title'], 't32')
        self.assertEqual(response.data['results'][1]['title'], 't31')
        self.assertEqual(response.data['results'][2]['title'], 't30')
        self.assertEqual(response.data['results'][3]['title'], 't23')
        self.assertEqual(response.data['results'][4]['title'], 't22')
        self.assertEqual(response.data['results'][5]['title'], 't21')
        self.assertEqual(response.data['results'][6]['title'], 't20')
        self.assertEqual(response.data['results'][7]['title'], 't14')
        self.assertEqual(response.data['results'][8]['title'], 't13')
        self.assertEqual(response.data['results'][9]['title'], 't12')

    def test_approve(self):
        """
        we can approve event through API
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

        e = EventFactory()

        url = prepare_url('admin-events-approve', kwargs={'id': str(e.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.status, Event.APPROVED)

    def test_reject(self):
        """
        we can reject event through API
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

        e = EventFactory()
        count = len(e.rejection_reasons)

        data = {
            'text': 'Disgusting',
        }

        url = prepare_url('admin-events-reject', kwargs={'id': str(e.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        e = Event.objects.get(id=e.id)
        self.assertEqual(e.status, Event.REJECTED)
        self.assertEqual(len(e.rejection_reasons), count+1)

    def test_activate(self):
        """
        we can activate event through API
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

        i = EventFactory(is_active=False)

        url = prepare_url('admin-events-activate', kwargs={'id': str(i.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        i = Event.objects.get(id=i.id)
        self.assertTrue(i.is_active)

    def test_deactivate(self):
        """
        we can deactivate event through API
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

        i = EventFactory(is_active=True)

        url = prepare_url('admin-events-deactivate', kwargs={'id': str(i.id)})
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        i = Event.objects.get(id=i.id)
        self.assertFalse(i.is_active)
