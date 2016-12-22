from rest_framework import mixins
from rest_framework_mongoengine import viewsets

from happ.models import FeedbackMessage
from happ.policies import StaffPolicy
from happ.serializers import FeedbackMessageSerializer


class FeedbackMessageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = FeedbackMessageSerializer
    queryset = FeedbackMessage.objects.all().order_by('-date_created')

    def retrieve(self, request, *args, **kwargs):
        response = super(FeedbackMessageViewSet, self).retrieve(request, *args, **kwargs)
        response.template_name = 'admin/feedback/detail.html'
        return response

    def list(self, request, *args, **kwargs):
        response = super(FeedbackMessageViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/feedback/list.html'
        return response
