from rest_framework import serializers


class RoundedField(serializers.DecimalField):
    """Used to automatically round decimals."""

    def __init__(self, max_digits=255, decimal_places=2, **kwargs):
        super().__init__(max_digits, decimal_places, **kwargs)

    def validate_precision(self, value):
        return value
