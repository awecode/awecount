from rest_framework import serializers


class ShortNameChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)
        extra_fields = self.context.get('extra_fields')

        if extra_fields:
            for field, field_type in extra_fields.items():
                self.fields[field] = field_type()

    def get_name(self, obj):
        if hasattr(obj, 'short_name') and obj.short_name:
            return obj.short_name
        return obj.name
