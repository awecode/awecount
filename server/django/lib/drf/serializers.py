from django.db import models
from rest_framework import serializers


class DecimalField(serializers.DecimalField):
    def __init__(
        self,
        max_digits,
        decimal_places,
        coerce_to_string=None,
        max_value=None,
        min_value=None,
        localize=False,
        rounding=None,
        normalize_output=True,
        **kwargs,
    ):
        super().__init__(
            max_digits,
            decimal_places,
            coerce_to_string,
            max_value,
            min_value,
            localize,
            rounding,
            normalize_output,
            **kwargs,
        )


class BaseModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.serializer_field_mapping[models.DecimalField] = DecimalField
        super().__init__(*args, **kwargs)
