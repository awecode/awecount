from rest_framework import serializers

from apps.voucher.models import SalesSetting, PurchaseSetting


class SalesSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        exclude = ('company',)


class PurchaseSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ('company',)
