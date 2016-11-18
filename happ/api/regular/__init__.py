import os

from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.renderers import TemplateHTMLRenderer

from happ.models import FileObject
from happ.decorators import patch_permission_classes
from happ.integrations import google
from happ.serializers import FileObjectSerializer


class TempUploadView(APIView):
    """
    API endpoint for getting temporary file object
    """
    def post(self, request):
        file_objects = map(lambda y: FileObject.objects.create(path=y),
                    request.POST.getlist('files', [])
                )
        return Response(FileObjectSerializer(file_objects, many=True).data, status=status.HTTP_200_OK)


class EditableHTMLView(APIView):
    renderer_classes = (TemplateHTMLRenderer, )
    permission_classes = ()

    def get(self, request):
        return Response(template_name=self.template_name, status=status.HTTP_200_OK)

    @patch_permission_classes(api_settings.DEFAULT_PERMISSION_CLASSES)
    def post(self, request):
        text = request.data['text']
        path = os.path.join(settings.TEMPLATES_DIR_ROOT, self.template_name)
        with open(path, 'w') as f:
            f.write(text.encode('utf-8'))
        return Response(template_name=self.template_name, status=status.HTTP_200_OK)


class TermsOfServiceView(EditableHTMLView):
    """
    API endpoint for setting and getting terms of service
    """
    template_name = 'texts/terms_of_service.html'


class PrivacyPolicyView(EditableHTMLView):
    """
    API endpoint for setting and getting privacy policy
    """
    template_name = 'texts/privacy_policy.html'


class OrganizerRulesView(EditableHTMLView):
    """
    API endpoint for setting and getting organizer rules
    """
    template_name = 'texts/organizer_rules.html'


class GooglePlacesView(APIView):
    """
    API endpoint for retranslating google places search results to user
    """
    def post(self, request):
        text = request.data['text']
        r = google.places(text)
        return Response(r, status=status.HTTP_200_OK)
