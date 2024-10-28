from rest_framework import serializers

from apps.voucher.models import PaymentMode


class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ["id", "name", "is_credit"]
