from auditlog.models import LogEntry
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.aggregator.widgets import WIDGET_CHOICES
from awecount.utils.CustomViewSet import CRULViewSet
from awecount.utils.helpers import choice_parser
from .models import Widget, GROUP_BY, DISPLAY_TYPES
from .serializers import LogEntrySerializer, WidgetSerializer, WidgetUpdateSerializer


class LogEntryViewSet(ReadOnlyModelViewSet):
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        return LogEntry.objects.filter(actor__company_id=self.request.user.company_id).select_related('content_type',
                                                                                                      'actor')


class WidgetViewSet(CRULViewSet):
    serializer_class = WidgetSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return WidgetSerializer
        else:
            return WidgetUpdateSerializer

    @action(detail=False)
    def data(self, request):
        qs = self.get_queryset().filter(is_active=True)
        return Response(WidgetSerializer(qs, many=True).data)

    def get_queryset(self):
        return Widget.objects.filter(user=self.request.user).order_by('order', 'pk')

    def get_defaults(self, request=None):
        data = {
            'options': {
                'widgets': choice_parser(WIDGET_CHOICES),
                'groups': choice_parser(GROUP_BY),
                'display_types': choice_parser(DISPLAY_TYPES),
            },
        }
        return data
