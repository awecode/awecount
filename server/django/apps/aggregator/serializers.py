import json

from auditlog.models import LogEntry
from rest_framework import serializers
from rest_framework.exceptions import APIException

from lib.drf.serializers import BaseModelSerializer

from .models import Widget


class LogEntrySerializer(BaseModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    actor_id = serializers.ReadOnlyField()
    action = serializers.SerializerMethodField()
    datetime = serializers.SerializerMethodField()
    changes_obj = serializers.SerializerMethodField()

    def get_changes_obj(self, obj):
        if isinstance(obj.changes, (str, bytes, bytearray)):
            return json.loads(obj.changes)
        return obj.changes

    def get_datetime(self, obj):
        return "{:%x, %H:%M %p}".format(obj.timestamp)

    def get_action(self, obj):
        return obj.get_action_display().title()

    def get_actor(self, obj):
        return str(obj.actor)

    def get_content_type_name(self, obj):
        return obj.content_type.model_class()._meta.verbose_name.title()

    class Meta:
        model = LogEntry
        exclude = ("timestamp", "changes")


class WidgetSerializer(BaseModelSerializer):
    data = serializers.ReadOnlyField(source="get_data")

    class Meta:
        model = Widget
        exclude = ("user",)


class WidgetListSerializer(BaseModelSerializer):
    class Meta:
        model = Widget
        fields = (
            "id",
            "name",
            "widget",
            "order",
            "group_by",
            "count",
            "display_type",
            "is_active",
        )


class WidgetUpdateSerializer(BaseModelSerializer):
    def validate(self, data):
        if data.get("count") < 1:
            # TODO proper exception message
            raise APIException({"detail": "Count is set as 0"})
        data["user_id"] = self.context.get("request").user.id
        return data

    class Meta:
        model = Widget
        exclude = ("user", "name", "order")
