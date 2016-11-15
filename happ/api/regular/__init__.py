from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class TempUploadView(APIView):
    """
    API endpoint for getting temporary file url
    """
    def post(self, request):
        return Response(request.POST.getlist('files', []), status=status.HTTP_200_OK)
