import os

from django.conf import settings
from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.renderers import StaticHTMLRenderer

from happ.models import FileObject, Currency, StaticText
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
    renderer_classes = (StaticHTMLRenderer, )
    permission_classes = ()

    def get_static_text(self, request):
        try:
            st = StaticText.objects.get(type=self.type)
        except:
            st = StaticText(type=self.type)
        return st

    def get(self, request):
        st = self.get_static_text(request)
        return Response(st.text or '', status=status.HTTP_200_OK)

    @patch_permission_classes(api_settings.DEFAULT_PERMISSION_CLASSES)
    def post(self, request):
        text = request.data['text']
        st = self.get_static_text(request)
        st.text = text.encode('utf-8')
        st.save()
        return Response(status=status.HTTP_200_OK)


class TermsOfServiceView(EditableHTMLView):
    """
    API endpoint for setting and getting terms of service
    """
    type = StaticText.TERMS_OF_SERVICE


class PrivacyPolicyView(EditableHTMLView):
    """
    API endpoint for setting and getting privacy policy
    """
    type = StaticText.PRIVACY_POLICY


class OrganizerRulesView(EditableHTMLView):
    """
    API endpoint for setting and getting organizer rules
    """
    type = StaticText.ORGANIZER_RULES


class FAQView(EditableHTMLView):
    """
    API endpoint for setting and getting FAQ page
    """
    type = StaticText.FAQ


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


class AppRedirectView(APIView):
    """
    API endpoint for redirecting to app
    """
    permission_classes = ()

    def get(self, request):
        url = request.query_params.get('url', None)
        response = HttpResponse("", status=302)
        response['Location'] = "{}://{}".format(settings.HAPP_PREFIX, url)
        return response
