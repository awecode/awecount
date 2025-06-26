from rest_framework import serializers

from apps.ledger.models import Account
from apps.tax.models import TaxScheme
from lib.drf.serializers import BaseModelSerializer

from ..models import LandedCostRow, LandedCostRowType


class TaxSchemeSerializer(BaseModelSerializer):
    class Meta:
        model = TaxScheme
        fields = ["name", "rate", "short_name"]


class CreditAccountSerializer(BaseModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name"]


class LandedCostRowSerializer(BaseModelSerializer):
    """Serializer for LandedCostRow model."""

    id = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(choices=LandedCostRowType.choices)

    tax_scheme = TaxSchemeSerializer(read_only=True)
    tax_scheme_id = serializers.PrimaryKeyRelatedField(
        source="tax_scheme",
        queryset=TaxScheme.objects.all(),
        required=False,
    )

    credit_account = CreditAccountSerializer(read_only=True)
    credit_account_id = serializers.PrimaryKeyRelatedField(
        source="credit_account",
        queryset=Account.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate(self, data):
        """
        Custom validation to ensure credit_account_id is provided
        unless the type is CUSTOMS_VALUATION_UPLIFT.
        """
        landed_cost_type = data.get("type")
        if (
            landed_cost_type != LandedCostRowType.CUSTOMS_VALUATION_UPLIFT
            and data.get("credit_account_id") is None
            and data.get("credit_account") is None
        ):
            raise serializers.ValidationError(
                {
                    "credit_account_id": "This field may not be null."
                }
            )
        return data

    class Meta:
        model = LandedCostRow
        fields = [
            "id",
            "type",
            "description",
            "amount",
            "is_percentage",
            "value",
            "tax_scheme",
            "tax_scheme_id",
            "credit_account",
            "credit_account_id",
            "tax_amount",
            "currency",
            "total_amount",
        ]
        extra_kwargs = {
            "tax_amount": {"read_only": True},
            "total_amount": {"read_only": True},
        }
