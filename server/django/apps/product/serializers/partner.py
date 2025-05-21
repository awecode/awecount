from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.product.models import Item


class PartnerItemSerializer(ModelSerializer):
    current_balance = SerializerMethodField()

    def get_current_balance(self, obj):
        return (obj.account.current_dr - obj.account.current_cr) if obj.account else None

    class Meta:
        model = Item
        fields = ["code", "current_balance"]
