from rest_framework import serializers
from rest_framework.exceptions import ValidationError


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


class StatusReversionMixin(object):
    UNISSUED_TYPES = ['Unapproved', 'Cancelled', 'Draft']

    def validate_voucher_status(self, validated_data, instance):
        if instance.status not in self.UNISSUED_TYPES and validated_data.get('status') in self.UNISSUED_TYPES:
            raise ValidationError(
                {'detail': 'Issued voucher cannot be unissued.'},
            )


class DisableCancelEditMixin(object):
    CANCELLED_STATUSES = ['Canceled', 'Cancelled', ]

    def disable_cancel_edit(self, validated_data, instance):
        if instance.status in self.CANCELLED_STATUSES and validated_data.get('status') not in self.CANCELLED_STATUSES:
            raise ValidationError(
                {'detail': 'Cancelled vouchers cannot be reverted.'},
            )
