from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, qs_exists


class CustomUniqueTogetherValidator(UniqueTogetherValidator):
    def __call__(self, attrs):
        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset)
        queryset = self.exclude_current_instance(attrs, queryset)

        # Ignore validation if any field is None
        checked_values = [value for field, value in attrs.items() if field in self.fields]
        if qs_exists(queryset):
            field_names = ", ".join(self.fields)
            message = self.message.format(field_names=field_names)
            raise ValidationError(message, code="unique")
