import json

from auditlog.models import LogEntry
from rest_framework import serializers

from .models import Widget


class LogEntrySerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    actor_id = serializers.ReadOnlyField()
    action = serializers.SerializerMethodField()
    datetime = serializers.SerializerMethodField()
    changes_obj = serializers.SerializerMethodField()

    def get_changes_obj(self, obj):
        if obj.changes:
            return json.loads(obj.changes)
        return

    def get_datetime(self, obj):
        return "{:%x, %H:%M %p}".format(obj.timestamp)

    def get_action(self, obj):
        return obj.get_action_display().title()

    def get_actor(self, obj):
        return str(obj.actor)

    def get_content_type_name(self, obj):
        return obj.content_type.model.title()

    class Meta:
        model = LogEntry
        exclude = ('timestamp', 'changes')


class WidgetSerializer(serializers.ModelSerializer):
    data = serializers.ReadOnlyField(source='get_data')

    class Meta:
        model = Widget
        exclude = ('user',)
