from auditlog.models import LogEntry
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.aggregator.serializers import LogEntrySerializer


class LogEntryViewSet(ReadOnlyModelViewSet):
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        return LogEntry.objects.filter(actor__company_id=self.request.user.company_id).select_related('content_type', 'actor')
