from rest_framework import serializers

from apps.product.models import Item, Unit


class ItemSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField(required=False)

    class Meta:
        model = Item
        exclude = ('company', 'tax_scheme',)


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        exclude = ('company',)
