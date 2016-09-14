from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import User
from happ.policies import StaffPolicy, RootPolicy
from happ.decorators import patch_permission_classes
from happ.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        return super(UserViewSet, self).create(request, *args, **kwargs)
