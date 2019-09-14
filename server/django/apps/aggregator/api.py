from auditlog.models import LogEntry
from rest_framework.viewsets import ReadOnlyModelViewSet

from awecount.utils.CustomViewSet import CRULViewSet
from .models import Widget
from .serializers import LogEntrySerializer, WidgetSerializer, WidgetUpdateSerializer


class LogEntryViewSet(ReadOnlyModelViewSet):
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        return LogEntry.objects.filter(actor__company_id=self.request.user.company_id).select_related('content_type', 'actor')


class WidgetViewSet(CRULViewSet):
    serializer_class = WidgetSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return WidgetSerializer
        else:
            return WidgetUpdateSerializer

    @property
    def paginator(self):
        if self.action == 'list':
            return None

    def get_queryset(self):
        return Widget.objects.filter(user=self.request.user).order_by('order')
