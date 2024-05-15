from auditlog.models import LogEntry
from import_export import resources

from awecount.libs.resources import PrettyNameModelResource


class LogEntryResource(PrettyNameModelResource):
    user = resources.Field("actor__full_name", column_name="User")
    content_type = resources.Field("content_type__model", column_name="Type")

    class Meta:
        model = LogEntry
        exclude = (
            "actor",
            "actor_id",
        )
