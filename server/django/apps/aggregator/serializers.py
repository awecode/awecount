from auditlog.models import LogEntry
from rest_framework import serializers


class LogEntrySerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    actor_id = serializers.ReadOnlyField()
    action = serializers.SerializerMethodField()

    def get_action(self, obj):
        return obj.get_action_display().title()

    def get_actor(self, obj):
        return str(obj.actor)

    def get_content_type_name(self, obj):
        return obj.content_type.model.title()

    class Meta:
        model = LogEntry
        exclude = ()
