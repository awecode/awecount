from rest_framework import serializers

from apps.product.models import Item


class ItemSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField(required=False)

    class Meta:
        model = Item
        exclude = ('company', 'tax_scheme',)
