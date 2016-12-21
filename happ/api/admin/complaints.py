from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework_mongoengine import viewsets

from happ.models import Complaint
from happ.policies import StaffPolicy
from happ.serializers import ComplaintSerializer


class ComplaintViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (StaffPolicy, )
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all()

    def list(self, request, *args, **kwargs):
        response = super(ComplaintViewSet, self).list(request, *args, **kwargs)
        response.template_name = 'admin/complaints/list.html'
        return response

    @detail_route(methods=['post'], url_path='reply')
    def reply(self, request, *args, **kwargs):
        instance = self.get_object()
        answer = request.data.get('answer', '')
        executor = request.user
        instance.reply(answer=answer, executor=executor)

        return Response(status=status.HTTP_204_NO_CONTENT)
