import datetime

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.auth.utils import generate_confirmation_key
from happ.models import User
from happ.factories import UserFactory
from happ.tests import *


class Tests(APISimpleTestCase):

    def test_user_registration(self):
        """
        Registration resourse creates one user
        it creates embedded settings
        it returns JWT auth token
        """
        n = User.objects.count()
        url = prepare_url('register')
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

    def test_user_registration_same_username(self):
        """
        We cannot register user with existing username
        """
        n = User.objects.count()
        url = prepare_url('register')
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

        n = User.objects.count()
        url = prepare_url('register')
        data = {
            'username': 'username',
            'email': 'email@mail.com',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), n)

    def test_user_registration_no_username(self):
        """
        Ensures that we cannot register without username
        """
        n = User.objects.count()
        url = prepare_url('register')
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
        Ensures that we can register without email
        """
        n = User.objects.count()
        url = prepare_url('register')
        data = {
            'username': 'username',
            'password': '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='username')
        self.assertEqual(User.objects.count(), n+1)
        self.assertNotEqual(user.settings, None)
        self.assertIn('token', response.data)

    def test_user_registration_no_password(self):
        """
        Ensures that we cannot register without password
        """
        n = User.objects.count()
        url = prepare_url('register')
        data = {
            'username': 'username',
            'email': 'email@mail.com',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error_message', response.data)
        self.assertEqual(User.objects.count(), n)

    def test_user_facebook_registration(self):
        """
        Facebook registration resourse creates one user
        it creates embedded settings
        it returns JWT auth token
        """
        n = User.objects.count()
        url = prepare_url('facebook-register')
        data = {
            'facebook_id': '123456',
            'fullname': 'Richard Green',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='123456')
        self.assertEqual(User.objects.count(), n+1)
        self.assertNotEqual(user.settings, None)
        self.assertIn('token', response.data)

    def test_user_registration_same_facebook_id(self):
        """
        We cannot register user with existing facebook_id
        """
        n = User.objects.count()
        url = prepare_url('facebook-register')
        data = {
            'facebook_id': '123456',
            'fullname': 'Richard Green',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='123456')
        self.assertEqual(User.objects.count(), n+1)
        self.assertNotEqual(user.settings, None)
        self.assertIn('token', response.data)

        n = User.objects.count()
        url = prepare_url('facebook-register')
        data = {
            'facebook_id': '123456',
            'fullname': 'Richard Green',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), n)

    def test_user_registration_no_facebook_id(self):
        """
        Ensures that we cannot register without facebook_id
        """
        n = User.objects.count()
        url = prepare_url('facebook-register')
        data = {
            'fullname': 'Richard Green',
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

        auth_url = prepare_url('login')
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

        url = prepare_url('password-reset')

        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'email': u.email,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_reset_confirm(self):
        """
        Ensures that user can confirm password reset
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = prepare_url('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'token': default_token_generator.make_token(u),
            'new_password': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_reset_confirm_no_uidb64(self):
        """
        Ensures that user cannot confirm password reset without uidb64
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = prepare_url('password-reset-confirm')

        data = {
            'token': default_token_generator.make_token(u),
            'new_password': '1234567a',
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

        url = prepare_url('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'new_password': '1234567a',
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

        url = prepare_url('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u2.pk)),
            'token': default_token_generator.make_token(u),
            'new_password': '1234567a',
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

        url = prepare_url('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'token': default_token_generator.make_token(u2),
            'new_password': '1234567a',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password(self):
        """
        We can change user's password
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = prepare_url('password-change')

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['token'], None)
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        data = {
            'old_password': '123',
            'new_password': '1234qwerASDF!@#$',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data = {
            'username': u.username,
            'password': '1234qwerASDF!@#$'
        }
        response = self.client.post(auth_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['token'], None)

    def test_change_password_wrong_old(self):
        """
        We cannot change user's password with wrong old password
        """
        u = UserFactory()
        u.set_password('123')
        u.save()

        url = prepare_url('password-change')

        auth_url = prepare_url('login')
        data = {
            'username': u.username,
            'password': '123'
        }
        response = self.client.post(auth_url, data=data, format='json')
        token = response.data['token']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['token'], None)
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        data = {
            'old_password': '1234',
            'new_password': '1234qwerASDF!@#$',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_confirm_request(self):
        """
        Ensures that user send email confirmation request
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
        self.client.credentials(HTTP_AUTHORIZATION='{} {}'.format(api_settings.JWT_AUTH_HEADER_PREFIX, token))

        url = prepare_url('email-confirm-request')

        response = self.client.get(url, format='json')
        u = User.objects.get(id=u.id)
        self.assertNotEqual(u.confirmation_key, None)
        self.assertNotEqual(u.confirmation_key_expires, None)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        u.email = None
        u.save()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_confirm(self):
        """
        Ensures that user can confirm email
        """
        u = UserFactory(role=User.REGULAR)
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

        url = prepare_url('email-confirm-request')
        response = self.client.get(url, format='json')
        u = User.objects.get(id=u.id)

        url = prepare_url('email-confirm')

        data = {
            'key': u.confirmation_key
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        u = User.objects.get(id=u.id)
        self.assertEqual(u.role, User.ORGANIZER)
        self.assertEqual(u.confirmation_key, None)
        self.assertEqual(u.confirmation_key_expires, None)

    def test_email_confirm_no_key(self):
        """
        Ensures that user cannot confirm email with no key provided
        """
        u = UserFactory(role=User.REGULAR)
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

        url = prepare_url('email-confirm-request')
        response = self.client.get(url, format='json')
        u = User.objects.get(id=u.id)

        url = prepare_url('email-confirm')

        data = {}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_confirm_wrong_key(self):
        """
        Ensures that user cannot confirm email with wrong key provided
        """
        u = UserFactory(role=User.REGULAR)
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

        url = prepare_url('email-confirm-request')
        response = self.client.get(url, format='json')
        u = User.objects.get(id=u.id)

        url = prepare_url('email-confirm')

        data = {
            'key': u.confirmation_key+'123'
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_confirm_key_expired(self):
        """
        Ensures that user cannot confirm email with expired key
        """
        u = UserFactory(role=User.REGULAR)
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

        url = prepare_url('email-confirm-request')
        response = self.client.get(url, format='json')
        u = User.objects.get(id=u.id)
        u.confirmation_key_expires = u.confirmation_key_expires - datetime.timedelta(days=settings.CONFIRMATION_KEY_EXPIRES)
        u.save()

        url = prepare_url('email-confirm')

        data = {
            'key': u.confirmation_key
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_facebook_login(self):
        """
        Login with facebook
        it returns JWT auth token
        """
        facebook_id = '123'
        u = UserFactory(facebook_id=facebook_id)
        url = prepare_url('facebook-login')
        data = {
            'facebook_id': facebook_id,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_facebook_login_no_facebook_id(self):
        """
        cannot auth if no facebook_id provided
        """
        facebook_id = '123'
        u = UserFactory(facebook_id=facebook_id)
        url = prepare_url('facebook-login')
        data = {
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_facebook_login_wrong_facebook_id(self):
        """
        cannot auth if such facebook_id is not registered
        """
        facebook_id = '123'
        u = UserFactory(facebook_id=facebook_id)
        url = prepare_url('facebook-login')
        data = {
            'facebook_id': facebook_id + '123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
