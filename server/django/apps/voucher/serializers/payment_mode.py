from rest_framework import serializers

from apps.ledger.serializers import AccountListSerializer
from apps.voucher.models import PaymentMode


class PaymentModeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = [
            "name",
            "enabled_for_sales",
            "enabled_for_purchase",
            "account",
            "transaction_fee_config",
            "transaction_fee_account",
        ]


class PaymentModeRetrieveSerializer(serializers.ModelSerializer):
    selected_account_obj = AccountListSerializer(source="account", read_only=True)
    selected_transaction_fee_account_obj = AccountListSerializer(
        source="transaction_fee_account", read_only=True
    )

    class Meta:
        model = PaymentMode
        fields = [
            "id",
            "name",
            "enabled_for_sales",
            "enabled_for_purchase",
            "account",
            "transaction_fee_config",
            "transaction_fee_account",
            "selected_account_obj",
            "selected_transaction_fee_account_obj",
        ]


class PaymentModeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = [
            "id",
            "name",
        ]
