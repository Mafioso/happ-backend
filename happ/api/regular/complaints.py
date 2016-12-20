from rest_framework import mixins
from rest_framework_mongoengine import viewsets

from happ.models import Complaint
from happ.serializers import ComplaintSerializer


class ComplaintViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.filter(author=self.request.user)
