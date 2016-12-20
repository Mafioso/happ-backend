import os

from django.conf import settings
from django.http.response import HttpResponse
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.renderers import TemplateHTMLRenderer

from happ.models import FileObject, Currency
from happ.decorators import patch_permission_classes
from happ.integrations import google, yahoo
from happ.serializers import FileObjectSerializer


class VersionView(APIView):
    """
    API endpoint for gettings current backend version number
    """
    def get(self, request):
        with open(os.path.join(settings.BASE_DIR, 'VERSION')) as f:
            version = f.read().strip()
        return Response({'version': version}, status=status.HTTP_200_OK)


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


class FAQView(EditableHTMLView):
    """
    API endpoint for setting and getting FAQ page
    """
    template_name = 'texts/faq.html'


class GooglePlacesView(APIView):
    """
    API endpoint for retranslating google places search results to user
    """
    def post(self, request):
        text = request.data.get('text', None)
        r = google.places(text.encode('utf-8'))
        return Response(r, status=status.HTTP_200_OK)


class GooglePhotosView(APIView):
    """
    API endpoint for retranslating google photos results
    """
    def get(self, request):
        photoreference = request.query_params.get('photoreference', None)
        max_width = request.query_params.get('max_width', 100)
        r = google.photos(photoreference, max_width)
        return HttpResponse(r, content_type="image/png")
        # Response(r, content_type='image/*', status=status.HTTP_200_OK)


class YahooExchangeView(APIView):
    """
    API endpoint for currency exchange using yahoo service
    """
    def post(self, request):
        amount = request.data.get('amount', 0)
        try:
            source_currency = Currency.objects.get(id=request.data.get('source'))
        except Currency.DoesNotExist:
            return Response(
                {'error_message': _('Wrong source currency.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            target_currency = Currency.objects.get(id=request.data.get('target'))
        except Currency.DoesNotExist:
            return Response(
                {'error_message': _('Wrong target currency.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = yahoo.exchange(source=source_currency.code,
                                target=target_currency.code,
                                amount=amount)
        if result:
            return Response({'result': result}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error_message': _('Remote service error.')},
                status=status.HTTP_400_BAD_REQUEST
            )
