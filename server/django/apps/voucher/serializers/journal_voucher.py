from decimal import Decimal

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError

from awecount.libs import decimalize
from awecount.libs.serializers import DisableCancelEditMixin
from awecount.libs.CustomViewSet import GenericSerializer

from ..models.journal_vouchers import JournalVoucher, JournalVoucherRow


class JournalVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    account_id = serializers.IntegerField(source="account.id", required=True)

    class Meta:
        model = JournalVoucherRow
        exclude = (
            "account",
            "journal_voucher",
        )


class JournalVoucherCreateSerializer(
    DisableCancelEditMixin, serializers.ModelSerializer
):
    rows = JournalVoucherRowSerializer(many=True)

    def validate(self, attrs):
        #  Raise error if both dr and cr in a row are 0
        for row in attrs.get("rows"):
            dr_amt = row.get("dr_amount")
            cr_amt = row.get("cr_amount")
            if not bool(dr_amt) and not bool(cr_amt):
                raise ValidationError({"detail": "Both Dr and Cr amounts cannot be 0."})

        # Raise error if debit and credit totals differ
        dr_total = Decimal(0)
        cr_total = Decimal(0)
        for row in attrs.get("rows"):
            dr = row.get("dr_amount")
            cr = row.get("cr_amount")
            if dr:
                dr_total += decimalize(dr)
            if cr:
                cr_total += decimalize(cr)
        if not (dr_total == cr_total):
            raise ValidationError({"detail": "Debit and Credit totals do not match."})

        return super().validate(attrs)

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        validated_data["company_id"] = self.context["request"].company.id
        journal_voucher = JournalVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop("account")
            row["account_id"] = account.get("id")
            JournalVoucherRow.objects.create(journal_voucher=journal_voucher, **row)
        JournalVoucher.apply_transactions(journal_voucher)
        return journal_voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        validated_data["company_id"] = self.context["request"].company.id
        self.disable_cancel_edit(validated_data, instance)
        JournalVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop("account")
            row["account_id"] = account.get("id")
            row["journal_voucher"] = instance
            try:
                JournalVoucherRow.objects.update_or_create(
                    pk=row.get("id"), defaults=row
                )
            except IntegrityError:
                raise APIException(
                    {"non_field_errors": ["Voucher repeated in journal voucher."]}
                )
        instance.refresh_from_db()
        JournalVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = JournalVoucher
        exclude = ("company",)


class JournalVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalVoucher
        fields = ("id", "voucher_no", "date", "status", "narration")


class JournalVoucherRowDetailSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source="account.name")
    selected_account_obj = GenericSerializer(read_only=True, source="account")

    class Meta:
        model = JournalVoucherRow
        fields = ("id", "account_id", "account_name", "type", "dr_amount", "cr_amount", "selected_account_obj")


class JournalVoucherDetailSerializer(serializers.ModelSerializer):
    rows = JournalVoucherRowDetailSerializer(many=True)

    class Meta:
        model = JournalVoucher
        fields = ("id", "voucher_no", "date", "status", "rows", "narration")
