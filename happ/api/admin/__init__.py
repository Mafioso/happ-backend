from rest_framework.views import APIView
from rest_framework.response import Response

from happ.policies import StaffPolicy
from happ.integrations import google


class UrlShortenerView(APIView):
    """
    API endpoint for shortening url
    """
    permission_classes = (StaffPolicy, )

    def get(self, request, format=None):
        url = request.GET.get('url', None)
        if not url:
            return Response()
        shorten_url = google.url_shortener(url)['id']
        return Response(shorten_url, content_type='text/plain')
