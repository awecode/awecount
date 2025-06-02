from django.conf import settings
from rest_framework import serializers

from apps.bank.serializers import BankAccount, BankAccountMinSerializer
from apps.voucher.models.voucher_settings import PurchaseSetting, SalesSetting
from awecount.libs.helpers import get_full_file_url, get_relative_file_path
from lib.drf.serializers import BaseModelSerializer


class SalesCreateSettingSerializer(BaseModelSerializer):
    class Meta:
        model = SalesSetting
        fields = ("fields", "options")


class SalesUpdateSettingSerializer(BaseModelSerializer):
    class Meta:
        model = SalesSetting
        fields = ("options",)


class PurchaseCreateSettingSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseSetting
        fields = ("fields", "options")


class PurchaseUpdateSettingSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseSetting
        fields = ("options",)


class PurchaseSettingCreateSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseSetting
        exclude = ("company",)


class PurchaseSettingSerializer(BaseModelSerializer):
    mode = serializers.SerializerMethodField()
    selected_mode_obj = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseSetting
        exclude = ("company",)

    def get_mode(self, obj):
        if obj.mode not in ["Cash", "Credit"]:
            return int(obj.mode)
        return obj.mode

    def get_selected_mode_obj(self, obj):
        if obj.mode not in ["Cash", "Credit"]:
            bank_account = BankAccount.objects.filter(id=obj.mode).first()
            return BankAccountMinSerializer(bank_account, many=False).data
        return None


class SalesSettingCreateSerializer(BaseModelSerializer):
    default_email_attachments = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        max_length=settings.MAX_DEFAULT_EMAIL_ATTACHMENTS,
    )

    def validate_default_email_attachments(self, value):
        return [get_relative_file_path(file) for file in value]

    class Meta:
        model = SalesSetting
        exclude = ("company",)


class SalesSettingsSerializer(BaseModelSerializer):
    mode = serializers.SerializerMethodField()
    selected_mode_obj = serializers.SerializerMethodField()
    default_email_attachments = serializers.SerializerMethodField()

    class Meta:
        model = SalesSetting
        exclude = ("company", "enable_sales_date_edit")

    def get_default_email_attachments(self, obj):
        request = self.context.get("request")
        return [
            get_full_file_url(request, file) for file in obj.default_email_attachments
        ]

    def get_mode(self, obj):
        if obj.mode not in ["Cash", "Credit"]:
            return int(obj.mode)
        return obj.mode

    def get_selected_mode_obj(self, obj):
        if obj.mode not in ["Cash", "Credit"]:
            bank_account = BankAccount.objects.filter(id=obj.mode).first()
            return BankAccountMinSerializer(bank_account, many=False).data
        return None
