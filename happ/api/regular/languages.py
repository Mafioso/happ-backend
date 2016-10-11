from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets


class LanguageViewSet(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        languages = settings.HAPP_LANGUAGES_VERBOSE
        return Response(languages, status=status.HTTP_200_OK)
