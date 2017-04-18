from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from apps.core.views import ChoicesViewSet
from apps.core.permissions import HasModelPermission

from apps.domain.models import Attribute
from apps.options.models import OptionSet
from apps.projects.models import Snapshot

from .models import Condition
from .serializers import (
    ConditionSerializer,
    ConditionIndexSerializer,
    AttributeSerializer,
    OptionSetSerializer
)


class ConditionViewSet(ModelViewSet):
    permission_classes = (HasModelPermission, )

    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    @list_route()
    def index(self, request):
        queryset = Condition.objects.all()
        serializer = ConditionIndexSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route()
    def resolve(self, request, pk):
        snapshot_id = request.GET.get('snapshot')

        if snapshot_id is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            condition = Condition.objects.get(pk=pk)
        except Condition.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        snapshot = Snapshot.objects.filter(project__user=request.user).get(pk=snapshot_id)

        result = condition.resolve(snapshot)
        return Response({'result': result})


class AttributeViewSet(ReadOnlyModelViewSet):
    permission_classes = (HasModelPermission, )
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer


class OptionSetViewSet(ReadOnlyModelViewSet):
    permission_classes = (HasModelPermission, )
    queryset = OptionSet.objects.order_by('order')
    serializer_class = OptionSetSerializer


class RelationViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Condition.RELATION_CHOICES
