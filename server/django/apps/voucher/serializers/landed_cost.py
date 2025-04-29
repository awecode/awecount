from rest_framework import serializers
from lib.drf.serializers import BaseModelSerializer

from ..models import LandedCostRow, LandedCostRowType


class LandedCostRowSerializer(BaseModelSerializer):
    """Serializer for LandedCostRow model."""

    type = serializers.ChoiceField(choices=LandedCostRowType.choices)
    # is_percentage = serializers.BooleanField(default=False)
    # currency = serializers.CharField(max_length=3, default="USD")
    # fixed_amount = serializers.DecimalField(
    #     max_digits=24, decimal_places=6, read_only=True
    # )

    class Meta:
        model = LandedCostRow
        fields = ["type", "description", "amount"]
