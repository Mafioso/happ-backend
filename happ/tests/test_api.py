from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from ..models import User, City, Currency, Event
from ..factories import UserFactory, CityFactory, CurrencyFactory


class CitiesTests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = reverse('cities-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        """
        Resourse is available with authentication only
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        
        url = reverse('cities-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, response.data['token']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CurrenciesTests(APISimpleTestCase):

    def test_get_without_auth(self):
        """
        Resourse is not available without authentication
        """
        url = reverse('currencies-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_with_auth(self):
        """
        Resourse is available with authentication only
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        
        url = reverse('currencies-list')
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, response.data['token']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthTests(APISimpleTestCase):

    def test_user_registration(self):
        """
        Registration resourse creates one user
        it creates embedded settings
        it returns JWT auth token
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'username': 'username',
            'email': 'email@mail.com',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='username')
        self.assertEqual(User.objects.count(), n+1)
        self.assertNotEqual(user.settings, None)
        self.assertIn('token', response.data)

    def test_user_registration_no_username(self):
        """
        Ensures that we cannot register without username
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'email': 'email@mail.com',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(User.objects.count(), n)

    def test_user_registration_no_email(self):
        """
        Ensures that we cannot register without email
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'username': 'username',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(User.objects.count(), n)

    def test_user_registration_no_password(self):
        """
        Ensures that we cannot register without password
        """
        n = User.objects.count()
        url = reverse('register')
        data = {
            'username': 'username',
            'email': 'email@mail.com',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(User.objects.count(), n)

    def test_authentication(self):
        """
        Ensures that user can authenticate with his username and password
        it returns JWT
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['token'], None)

        data = {
            'username': u.username,
            'password': '1234'
        }
        response = self.client.post(auth_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_password_reset(self):
        """
        Ensures that user can reset password
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = reverse('password-reset')

        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'email': u.email,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm(self):
        """
        Ensures that user can confirm password reset
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = reverse('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'token': default_token_generator.make_token(u),
            'new_password1': '1234567a',
            'new_password2': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_no_uidb64(self):
        """
        Ensures that user cannot confirm password reset without uidb64
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = reverse('password-reset-confirm')

        data = {
            'token': default_token_generator.make_token(u),
            'new_password1': '1234567a',
            'new_password2': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_no_token(self):
        """
        Ensures that user cannot confirm password reset without token
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = reverse('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'new_password1': '1234567a',
            'new_password2': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_password_mismatch(self):
        """
        Ensures that user cannot confirm password reset when two password are different
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = reverse('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'token': default_token_generator.make_token(u),
            'new_password1': '1234567a',
            'new_password2': '1234567b',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_wrong_uidb64(self):
        """
        Ensures that user cannot confirm password reset with wrong uidb64
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        u2 = UserFactory()
        u2.set_password('123')
        u2.save()

        url = reverse('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u2.pk)),
            'token': default_token_generator.make_token(u),
            'new_password1': '1234567a',
            'new_password2': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_wrong_token(self):
        """
        Ensures that user cannot confirm password reset with wrong token
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        u2 = UserFactory()
        u2.set_password('123')
        u2.save()

        url = reverse('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'token': default_token_generator.make_token(u2),
            'new_password1': '1234567a',
            'new_password2': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EventTests(APISimpleTestCase):

    def test_create_event(self):
        """
        We can create event
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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

        auth_url = reverse('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']

        url = reverse('events-list')
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
