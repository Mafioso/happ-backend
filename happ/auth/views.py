from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from happ.serializers import UserSerializer, UserPayloadSerializer

from .forms import HappPasswordResetForm

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
