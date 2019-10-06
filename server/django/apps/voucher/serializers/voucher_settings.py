from rest_framework import serializers

from apps.voucher.models import SalesSetting, PurchaseSetting


class SalesCreateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        fields = ('fields', 'options')


class SalesUpdateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        fields = ('options',)


class PurchaseCreateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        fields = ('fields', 'options')


class PurchaseUpdateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        fields = ('options',)


class PurchaseSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ('company',)


class SalesSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        exclude = ('company',)
