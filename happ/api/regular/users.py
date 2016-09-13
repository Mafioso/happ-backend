from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_mongoengine import viewsets

from happ.models import User
from happ.serializers import UserSerializer


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

    @list_route(methods=['post'], url_path='current/set/language')
    def set_language(self, request, *args, **kwargs):
        user = request.user
        if 'language' not in request.data:
            return Response(
                {'error_message': _('You should provide language to be set.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        language = request.data['language']
        if language not in settings.HAPP_LANGUAGES:
            return Response(
                {'error_message': _('Wrong language code.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.settings.language = language
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
