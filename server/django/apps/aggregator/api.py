from auditlog.models import LogEntry
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Widget
from .serializers import LogEntrySerializer, WidgetSerializer


class LogEntryViewSet(ReadOnlyModelViewSet):
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        return LogEntry.objects.filter(actor__company_id=self.request.user.company_id).select_related('content_type', 'actor')


class WidgetViewSet(ReadOnlyModelViewSet):
    serializer_class = WidgetSerializer

    def get_queryset(self):
        return Widget.objects.filter(user=self.request.user)
