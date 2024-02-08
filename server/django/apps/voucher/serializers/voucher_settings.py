from rest_framework import serializers

from apps.voucher.models import PurchaseSetting, SalesSetting


class SalesCreateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        fields = ("fields", "options")


class SalesUpdateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        fields = ("options",)


class PurchaseCreateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        fields = ("fields", "options")


class PurchaseUpdateSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        fields = ("options",)


class PurchaseSettingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ("company",)

    # def update(self, instance, validated_data):
    #     import ipdb; ipdb.set_trace()
    #     return super().update(instance, validated_data)


class PurchaseSettingSerializer(serializers.ModelSerializer):
    mode = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseSetting
        exclude = ("company",)

    def get_mode(self, obj):
        if obj.mode not in ["Cash", "Credit"]:
            return int(obj.mode)
        return obj.mode


class SalesSettingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSetting
        exclude = ("company",)


class SalesSettingsSerializer(serializers.ModelSerializer):
    mode = serializers.SerializerMethodField()

    class Meta:
        model = SalesSetting
        exclude = ("company", "enable_sales_date_edit")

    def get_mode(self, obj):
        if obj.mode not in ["Cash", "Credit"]:
            return int(obj.mode)
        return obj.mode
