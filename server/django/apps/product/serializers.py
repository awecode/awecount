from rest_framework import serializers

from apps.product.models import Item


class ItemSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = Item
        exclude = ('company',)
