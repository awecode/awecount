from rest_framework import serializers


class ShortNameChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        if hasattr(obj, 'short_name') and obj.short_name:
            return obj.short_name
        return obj.name
