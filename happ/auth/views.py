from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from happ.serializers import UserSerializer, UserPayloadSerializer

from .forms import HappPasswordResetForm, HappSetPasswordForm

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserRegister(CreateAPIView):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        """
        Once user created this endpoint returns JSON Web Token in response
        """
        if 'email' not in request.data or 'password' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        payload = jwt_payload_handler(serializer.instance)
        token = jwt_encode_handler(payload)
        return Response({'token': token}, status=status.HTTP_201_CREATED, headers=headers)


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
            return Response({'status': True}, status=status.HTTP_200_OK)

        return Response({'status': False}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirm(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, format=None):
        UserModel = get_user_model()
        uidb64 = request.data.pop('uidb64', None)
        token = request.data.pop('token', None)
        if not uidb64:
            return Response({'status': False}, status=status.HTTP_400_BAD_REQUEST)
        if not token:
            return Response({'status': False}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({'status': True}, status=status.HTTP_200_OK)
            return Response({'status': False}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': False}, status=status.HTTP_400_BAD_REQUEST)
