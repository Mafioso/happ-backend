from rest_framework import mixins
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets

from happ.models import LogEntry, User
from happ.policies import StaffPolicy
from happ.serializers import LogEntrySerializer


class LogEntryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = LogEntrySerializer
    queryset = LogEntry.objects.all().order_by('-date_created')

    def list(self, request, *args, **kwargs):
        response = super(LogEntryViewSet, self).list(request, *args, **kwargs)
        response.data['page'] = int(request.GET.get('page', 1))
        response.data['roles'] = User.get_roles_dict()
        response.template_name = 'admin/log/list.html'
        return response
