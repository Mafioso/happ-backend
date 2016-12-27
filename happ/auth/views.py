import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings

from happ.utils import send_mail
from happ.models import User
from happ.serializers import UserSerializer, UserPayloadSerializer

from .forms import HappPasswordResetForm, HappSetPasswordForm, PasswordChangeForm
from .utils import generate_confirmation_key

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class UserRegister(CreateAPIView):
    UserModel = get_user_model()
    serializer_class = UserSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        """
        Once user created this endpoint returns JSON Web Token in response
        """
        if 'username' not in request.data:
            return Response(
                {'error_message': _('No username provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        # if 'email' not in request.data:
        #     return Response(
        #         {'error_message': _('No email provided.')},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        if 'password' not in request.data:
            return Response(
                {'error_message': _('No password provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            UserModel.objects.get(username=request.data['username'])
            return Response(
                {'error_message': _('Username already exists.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            pass
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        payload = jwt_payload_handler(serializer.instance)
        token = jwt_encode_handler(payload)
        return Response({'token': token}, status=status.HTTP_201_CREATED, headers=headers)


class FacebookUserRegister(CreateAPIView):
    UserModel = get_user_model()
    serializer_class = UserSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        """
        Creates user using data from facebook
        Once user created this endpoint returns JSON Web Token in response
        - username => facebook_id
        - gender
        - fullname
        """
        if 'facebook_id' not in request.data:
            return Response(
                {'error_message': _('No facebook_id provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.data['username'] = request.data['facebook_id']
        try:
            UserModel.objects.get(username=request.data['username'])
            return Response(
                {'error_message': _('Username already exists.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            pass
        try:
            UserModel.objects.get(facebook_id=request.data['facebook_id'])
            return Response(
                {'error_message': _('Facebook_id already exists.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except:
            pass
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        payload = jwt_payload_handler(serializer.instance)
        token = jwt_encode_handler(payload)
        return Response({'token': token}, status=status.HTTP_201_CREATED, headers=headers)


class FacebookLogin(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        facebook_id = request.data.get('facebook_id', None)
        if not facebook_id:
            return Response(
                {'error_message': _('No facebook_id provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = get_user_model().objects.get(facebook_id=facebook_id)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({'token': token}, status=status.HTTP_201_CREATED)
        except:
            return Response(
                {'error_message': _('User does not exist.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordReset(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, format=None):
        """
        Submits form which, in turn, sends email with token
        """
        form = HappPasswordResetForm(request.data)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'request': request,
            }
            form.save(**opts)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
                {'error_message': _('Invalid data.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetConfirm(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, format=None):
        UserModel = get_user_model()
        uidb64 = request.data.pop('uidb64', None)
        token = request.data.pop('token', None)
        if not uidb64:
            return Response(
                {'error_message': _('uidb64 is not provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not token:
            return Response(
                {'error_message': _('token is not provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            form = HappSetPasswordForm(user, request.data)
            if form.is_valid():
                form.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error_message': _('Invalid data.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
                {'error_message': _('No such user or token is not valid.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordChange(APIView):
    def post(self, request, format=None):
        """
        Submits form which changes user password
        """
        print request.user
        form = PasswordChangeForm(user=request.user, data=request.data)
        if form.is_valid():
            form.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            print form._errors

        return Response(
                {'error_message': _('Invalid data.')},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailConfirmationRequest(APIView):

    def get(self, request, format=None):
        """
        Generates organizer mode confirmation key and sends email with it
        """
        user = request.user
        if not user.email:
            return Response(
                {'error_message': _('No email provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.confirmation_key = generate_confirmation_key(user)
        user.confirmation_key_expires = datetime.datetime.now() + datetime.timedelta(days=settings.CONFIRMATION_KEY_EXPIRES)
        user.save()
        domain = get_current_site(request).domain

        url = '{domain}{path}?key={key}'.format(
                domain=domain,
                path=reverse('email-confirm'),
                key=user.confirmation_key,
            )
        context = {
            'user': user,
            'domain': domain,
            'url': url,
        }

        send_mail(subject_template_name='happ/email_confirmation.txt',
                  email_template_name='happ/email_confirmation.html',
                  context=context,
                  from_email=None,
                  to_email=user.email,
                  html_email_template_name='happ/email_confirmation.html'
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailConfirmation(APIView):

    def post(self, request, format=None):
        """
        Confirms email and assigns Organizer role to user
        """
        key = request.data.pop('key', None)
        if not key:
            return Response(
                {'error_message': _('Confirmation key is not provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(confirmation_key=key)
        except User.DoesNotExist:
            return Response(
                {'error_message': _('Wrong confirmation key.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if datetime.datetime.now() > user.confirmation_key_expires:
            return Response(
                {'error_message': _('Confirmation key expired.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.confirmation_key = None
        user.confirmation_key_expires = None
        user.role = User.ORGANIZER
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminLogin(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            if user.role >= User.MODERATOR:
                token = serializer.object.get('token')
                response_data = jwt_response_payload_handler(token, user, request)

                return Response(response_data)
            return Response({'error_message': _('Cannot authenticate')}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
