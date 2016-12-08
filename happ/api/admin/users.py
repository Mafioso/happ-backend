from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets

from mongoextensions import filters
from happ.models import User
from happ.policies import StaffPolicy, RootAdministratorPolicy
from happ.decorators import patch_permission_classes, patch_queryset
from happ.serializers import UserAdminSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = UserAdminSerializer
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

    @patch_queryset(lambda self, x: x.filter(role__in=[User.REGULAR, User.ORGANIZER]))
    def list(self, request, *args, **kwargs):
        response = super(UserViewSet, self).list(request, *args, **kwargs)
        response.data['page'] = int(request.GET.get('page', 1))
        response.template_name = 'admin/users/list.html'

        return response

    def retrieve(self, request, *args, **kwargs):
        response = super(UserViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = 'admin/users/edit.html'
        return response

    @list_route(methods=['get'], url_path='organizers')
    @patch_queryset(lambda self, x: x.filter(role__in=[User.ORGANIZER]))
    def organizers(self, request, *args, **kwargs):
        response = super(UserViewSet, self).list(request, *args, **kwargs)
        response.data['page'] = int(request.GET.get('page', 1))
        response.template_name = 'admin/users/organizers.html'

        return response

    @detail_route(methods=['post'], url_path='activate')
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activate()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='deactivate')
    def deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deactivate()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['post'], url_path='change_password')
    def change_password(self, request, *args, **kwargs):
        instance = request.user

        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')
        new_password2 = request.data.get('new_password2', '')

        if new_password != new_password2:
            return Response(
                {'error_message': _("The two password fields didn't match.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not instance.check_password(old_password):
            return Response(
                {'error_message': _("Your old password was entered incorrectly. Please enter it again.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.set_password(new_password)
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
