from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets

from ..models import User
from ..serializers import UserSerializer


class UsersViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @list_route(methods=['get'], url_path='current')
    def current(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path='current/edit')
    def current_edit(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
