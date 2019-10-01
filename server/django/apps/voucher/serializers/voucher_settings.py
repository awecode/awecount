from rest_framework import serializers

from apps.voucher.models import SalesSetting, PurchaseSetting


class SalesSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        exclude = ('id', 'company',)


class PurchaseSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ('id', 'company',)
