from rest_framework import mixins
from rest_framework_mongoengine import viewsets

from happ.serializers import FeedbackMessageSerializer


class FeedbackMessageViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = FeedbackMessageSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
