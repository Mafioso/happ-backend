from rest_framework import mixins
from rest_framework_mongoengine import viewsets

from happ.models import Complaint
from happ.policies import StaffPolicy
from happ.serializers import ComplaintSerializer


class ComplaintViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all()

    def list(self, request, *args, **kwargs):
        response = super(ComplaintViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/complaints/list.html'
        return response
