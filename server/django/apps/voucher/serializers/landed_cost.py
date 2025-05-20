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

    class Meta:
        model = LandedCostRow
        fields = [
            "id",
            "type",
            "description",
            "amount",
            "tax_scheme",
            "tax_scheme_id",
            "credit_account",
            "credit_account_id",
            "tax_amount",
            "total_amount",
        ]
        extra_kwargs = {
            "tax_amount": {"read_only": True},
            "total_amount": {"read_only": True},
        }
