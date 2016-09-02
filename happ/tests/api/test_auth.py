from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.test import APISimpleTestCase
from rest_framework_jwt.settings import api_settings

from happ.models import User
from happ.factories import UserFactory
from .. import *


class AuthTests(APISimpleTestCase):

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
        Ensures that we cannot register without email
        """
        n = User.objects.count()
        url = prepare_url('register')
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
        url = prepare_url('register')
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

        url = prepare_url('password-reset-confirm')

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

        url = prepare_url('password-reset-confirm')

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

        url = prepare_url('password-reset-confirm')

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

        url = prepare_url('password-reset-confirm')

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

        url = prepare_url('password-reset-confirm')

        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(u.pk)),
            'token': default_token_generator.make_token(u2),
            'new_password1': '1234567a',
            'new_password2': '1234567a',
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
            'new_password1': '1234qwerASDF!@#$',
            'new_password2': '1234qwerASDF!@#$',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
            'new_password1': '1234qwerASDF!@#$',
            'new_password2': '1234qwerASDF!@#$',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """
        We cannot change user's password when passwords mismatch
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
            'new_password1': '1234qwerASDF!@#$',
            'new_password2': '1234qwerASDF!@',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
