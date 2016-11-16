from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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
