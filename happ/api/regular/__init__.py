import os

from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from happ.models import FileObject
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


class TermsOfServiceView(APIView):
    """
    API endpoint for setting and getting terms of service
    """
    renderer_classes = (TemplateHTMLRenderer, )
    template_name = 'texts/terms_of_service.html'

    def get(self, request):
        return Response(template_name=self.template_name, status=status.HTTP_200_OK)

    def post(self, request):
        text = request.data['text']
        path = os.path.join(settings.TEMPLATES_DIR_ROOT, self.template_name)
        with open(path, 'w') as f:
            f.write(text.encode('utf-8'))
        return Response(template_name=self.template_name, status=status.HTTP_200_OK)
