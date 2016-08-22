from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from happ.serializers import UserSerializer


class UserRegister(CreateAPIView):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = ()
