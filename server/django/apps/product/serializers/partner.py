from rest_framework import serializers

from apps.product.models import Item


class PartnerItemListSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(max_digits=24, decimal_places=6)

    class Meta:
        model = Item
        fields = ["code", "current_balance"]
