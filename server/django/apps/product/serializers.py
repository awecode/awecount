from rest_framework import serializers

from .models import Item, Unit, Category as InventoryCategory
from .validators import CustomUniqueTogetherValidator


class ItemSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = Item
        exclude = ('company', 'tax_scheme', 'unit',)
        validators = [
            CustomUniqueTogetherValidator(
                queryset=Item.objects.all(),
                fields=('code', 'company_id',),
                message="Item with code exists."
            )
        ]


class UnitSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = Unit
        exclude = ('company',)

class InventoryCategorySerializer(serializers.ModelSerializer):
    # company_id = serializers.IntegerField()
    class Meta:
        model = InventoryCategory
        exclude = ('company',)