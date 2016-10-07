from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import User
from happ.policies import StaffPolicy, RootAdministratorPolicy
from happ.decorators import patch_permission_classes
from happ.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        if 'role' in request.data:
            if request.data['role'] >= User.MODERATOR and request.user.role <= User.MODERATOR:
                return Response(
                    status=status.HTTP_403_FORBIDDEN
                )
            if request.data['role'] >= User.ADMINISTRATOR and request.user.role <= User.ADMINISTRATOR:
                return Response(
                    status=status.HTTP_403_FORBIDDEN
                )
            if request.data['role'] == User.ROOT:
                return Response(
                    status=status.HTTP_403_FORBIDDEN
                )
        return super(UserViewSet, self).create(request, *args, **kwargs)

    @patch_permission_classes(( RootAdministratorPolicy, ))
    def update(self, request, *args, **kwargs):
        if 'role' in request.data:
            if request.data['role'] >= User.ADMINISTRATOR and request.user.role <= User.ADMINISTRATOR:
                return Response(
                    status=status.HTTP_403_FORBIDDEN
                )
            if request.data['role'] == User.ROOT:
                return Response(
                    status=status.HTTP_403_FORBIDDEN
                )
        return super(UserViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.role >= User.MODERATOR and request.user.role <= User.MODERATOR:
                return Response(
                    status=status.HTTP_403_FORBIDDEN
                )
        if instance.role >= User.ADMINISTRATOR and request.user.role <= User.ADMINISTRATOR:
            return Response(
                status=status.HTTP_403_FORBIDDEN
            )
        if instance.role == User.ROOT:
            return Response(
                status=status.HTTP_403_FORBIDDEN
            )
        return super(UserViewSet, self).destroy(request, *args, **kwargs)
