from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.models.base import Account, Party


class ShortNameChoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)
        extra_fields = self.context.get("extra_fields")

        if extra_fields:
            for field, field_type in extra_fields.items():
                self.fields[field] = field_type()

    def get_name(self, obj):
        if hasattr(obj, "short_name") and obj.short_name:
            return obj.short_name
        return obj.name


class StatusReversionMixin(object):
    UNISSUED_TYPES = ["Unapproved", "Cancelled", "Draft"]

    def validate_voucher_status(self, validated_data, instance):
        if (
            instance.status not in self.UNISSUED_TYPES
            and validated_data.get("status") in self.UNISSUED_TYPES
        ):
            raise ValidationError(
                {"detail": "Issued voucher cannot be unissued."},
            )


class DisableCancelEditMixin(object):
    CANCELLED_STATUSES = [
        "Canceled",
        "Cancelled",
    ]

    def disable_cancel_edit(self, validated_data, instance):
        if (
            instance.status in self.CANCELLED_STATUSES
            and validated_data.get("status") not in self.CANCELLED_STATUSES
        ):
            raise ValidationError(
                {"detail": "Cancelled vouchers cannot be reverted."},
            )


class RoyaltyLedgerInfoPartySerializer(serializers.Serializer):
    tax_identification_number = serializers.CharField(required=True)
    name = serializers.CharField(required=True)

    royalty_amount = serializers.FloatField(required=True)
    tds_amount = serializers.FloatField(required=True)

    payable_account = None
    royalty_tds_account = None


class RoyaltyLedgerInfo(serializers.Serializer):
    royalty_expense_account_id = serializers.IntegerField(required=True)
    tds_category_id = serializers.IntegerField(required=True)
    parties = RoyaltyLedgerInfoPartySerializer(many=True, required=True)

    royalty_expense_account = None


class RoyaltyLedgerInfoSerializer(serializers.Serializer):
    royalty_ledger_info = RoyaltyLedgerInfo(required=False)

    extra_entries = None

    @transaction.atomic
    def validate_royalty_ledger_info(self, royalty_ledger_info):
        try:
            royalty_ledger_info["royalty_expense_account"] = Account.objects.get(
                id=royalty_ledger_info["royalty_expense_account_id"],
                company_id=self.context["request"].company.id,
            )
        except Account.DoesNotExist:
            raise ValidationError("Royalty expense account not found.")

        for royalty_party in royalty_ledger_info["parties"]:
            try:
                party = Party.objects.get(
                    tax_identification_number=royalty_party[
                        "tax_identification_number"
                    ],
                    company_id=self.context["request"].company.id,
                )
            except Party.DoesNotExist:
                party = Party(
                    name=royalty_party["name"],
                    tax_identification_number=royalty_party[
                        "tax_identification_number"
                    ],
                    company_id=self.context["request"].company.id,
                )
                party.save()
            except Party.MultipleObjectsReturned:
                raise ValidationError("Multiple parties found.")

            royalty_party["payable_account"] = party.supplier_account

            try:
                party_royalty_tds_account = Account.objects.get(
                    source=party.supplier_account,
                    category_id=royalty_ledger_info["tds_category_id"],
                    company_id=self.context["request"].company.id,
                )
            except Account.DoesNotExist:
                party_royalty_tds_account = Account(
                    name="Royalty TDS - " + party.name,
                    source=party.supplier_account,
                    category_id=royalty_ledger_info["tds_category_id"],
                    company_id=self.context["request"].company.id,
                )
                party_royalty_tds_account.save()
            except Account.MultipleObjectsReturned:
                raise ValidationError("Multiple party royalty TDS accounts found.")
            royalty_party["royalty_tds_account"] = party_royalty_tds_account

        return royalty_ledger_info
