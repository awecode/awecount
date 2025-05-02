from auditlog.models import LogEntry
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.aggregator.resources import LogEntryResource
from apps.aggregator.views import qs_to_xls
from apps.aggregator.widgets import WIDGET_CHOICES
from awecount.libs.CustomViewSet import CRULViewSet
from awecount.libs.helpers import choice_parser

from .models import DISPLAY_TYPES, GROUP_BY, Widget
from .serializers import (
    LogEntrySerializer,
    WidgetListSerializer,
    WidgetSerializer,
    WidgetUpdateSerializer,
)


class LogEntryViewSet(ReadOnlyModelViewSet):
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        return LogEntry.objects.filter(
            actor__member_company__company=self.request.company
        ).select_related("content_type", "actor")

    @action(detail=False)
    def export(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        params = [
            ("Audit Logs", queryset, LogEntryResource),
        ]
        return qs_to_xls(params)


class WidgetViewSet(CRULViewSet):
    serializer_class = WidgetSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return WidgetListSerializer
        return WidgetUpdateSerializer

    @action(detail=False)
    def data(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(is_active=True).order_by("-id")
        return Response(WidgetSerializer(qs, many=True).data)

    def get_queryset(self):
        # return Widget.objects.filter(user=self.request.user).order_by('order', 'pk')
        return Widget.objects.filter(user=self.request.user).order_by("-pk")

    @action(detail=True, methods=["POST"])
    def delete(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save()
        return Response({})

    def get_defaults(self, request=None, *args, **kwargs):
        data = {
            "options": {
                "widgets": choice_parser(WIDGET_CHOICES),
                "groups": choice_parser(GROUP_BY),
                "display_types": choice_parser(DISPLAY_TYPES),
            },
        }
        return data
