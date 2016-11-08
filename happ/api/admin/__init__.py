from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from happ.policies import StaffPolicy
from happ.integrations import google


class UrlShortenerView(APIView):
    """
    API endpoint for shortening url
    """
    permission_classes = (StaffPolicy, )

    def get(self, request):
        url = request.GET.get('url', None)
        if not url:
            return Response(
                {'error_message': _('No url provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        shorten_url = google.url_shortener(url)['id']
        return Response({'shorten_url': shorten_url})
