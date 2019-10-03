from rest_framework import serializers

from apps.voucher.models import SalesSetting, PurchaseSetting


class SalesCreateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        exclude = ('id', 'company',)


class SalesUpdateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        exclude = ('id', 'company', 'is_trade_discount_in_voucher', 'is_trade_discount_in_row', 'mode', 'bank_account')


class PurchaseCreateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ('id', 'company',)


class PurchaseUpdateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ('id', 'company', 'is_trade_discount_in_voucher', 'is_trade_discount_in_row', 'mode', 'bank_account')


class PurchaseSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseSetting
        fields = '__all__'
