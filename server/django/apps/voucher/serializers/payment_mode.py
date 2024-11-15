from rest_framework import serializers

from apps.ledger.serializers import AccountListSerializer
from apps.voucher.models import PaymentMode, TransactionFeeConfig


class PaymentModeCreateSerializer(serializers.ModelSerializer):
    def validate_transaction_fee_config(self, value):
        if not value:
            return

        try:
            TransactionFeeConfig(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return value

    def validate(self, data):
        if data.get("transaction_fee_config") and not data.get(
            "transaction_fee_account"
        ):
            raise serializers.ValidationError(
                "Transaction Fee Account is required if Transaction Fee Config is provided"
            )

        return

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

    def validate_transaction_fee_config(self, value):
        if not value:
            return

        try:
            TransactionFeeConfig(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return value

    def validate(self, data):
        if data.get("transaction_fee_config") and not data.get(
            "transaction_fee_account"
        ):
            raise serializers.ValidationError(
                "Transaction Fee Account is required if Transaction Fee Config is provided"
            )

        return

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
