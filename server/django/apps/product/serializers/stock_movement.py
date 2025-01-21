from rest_framework import serializers

from apps.product.models import Item


class StockMovementSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    opening_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    opening_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    purchase_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    purchase_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    purchase_return_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    purchase_return_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    production_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    production_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    sales_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    sales_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    sales_return_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    sales_return_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    consumption_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    consumption_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    stock_in_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    stock_in_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    stock_out_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    stock_out_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    closing_qty = serializers.DecimalField(max_digits=20, decimal_places=2)
    closing_value = serializers.DecimalField(max_digits=20, decimal_places=2)

    def get_unit(self, obj):
        return obj.unit.name if obj.unit else None

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "code",
            "unit",
            "account",
            "opening_qty",
            "opening_value",
            "purchase_qty",
            "purchase_value",
            "purchase_return_qty",
            "purchase_return_value",
            "production_qty",
            "production_value",
            "sales_qty",
            "sales_value",
            "sales_return_qty",
            "sales_return_value",
            "consumption_qty",
            "consumption_value",
            "stock_in_qty",
            "stock_in_value",
            "stock_out_qty",
            "stock_out_value",
            "closing_qty",
            "closing_value",
        ]
