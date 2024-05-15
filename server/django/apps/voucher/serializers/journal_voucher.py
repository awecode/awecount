from decimal import Decimal

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError

from apps.ledger.models.base import Account
from awecount.libs import decimalize, get_next_voucher_no
from awecount.libs.serializers import DisableCancelEditMixin

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
        validated_data["company_id"] = self.context["request"].company_id
        journal_voucher = JournalVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop("account")
            row["account_id"] = account.get("id")
            JournalVoucherRow.objects.create(journal_voucher=journal_voucher, **row)
        JournalVoucher.apply_transactions(journal_voucher)
        return journal_voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        validated_data["company_id"] = self.context["request"].company_id
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

    class Meta:
        model = JournalVoucherRow
        fields = ("id", "account_id", "account_name", "type", "dr_amount", "cr_amount")


class JournalVoucherDetailSerializer(serializers.ModelSerializer):
    rows = JournalVoucherRowDetailSerializer(many=True)

    class Meta:
        model = JournalVoucher
        fields = ("id", "voucher_no", "date", "status", "rows", "narration")


class PublicAccountSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    code = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    parent_id = serializers.IntegerField(required=False)
    parent__id = serializers.IntegerField(required=False)
    parent__code = serializers.CharField(required=False)
    parent__name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)
    category__id = serializers.IntegerField(required=False)
    category__name = serializers.CharField(required=False)
    category__code = serializers.CharField(required=False)
    supplier_detail__name = serializers.CharField(required=False)
    supplier_detail__email = serializers.EmailField(required=False)
    supplier_detail__contact_no = serializers.CharField(required=False)
    supplier_detail__tax_registration_number = serializers.IntegerField(required=False)
    customer_detail__name = serializers.CharField(required=False)
    customer_detail__email = serializers.EmailField(required=False)
    customer_detail__contact_no = serializers.CharField(required=False)
    customer_detail__tax_registration_number = serializers.IntegerField(required=False)


class PublicJournalVoucherRowSerializer(serializers.ModelSerializer):
    account = PublicAccountSerializer(default={})
    account_id = serializers.IntegerField(required=False)

    class Meta:
        model = JournalVoucherRow
        exclude = ("journal_voucher", "id")


class PublicJournalVoucherCreateSerializer(
    DisableCancelEditMixin, serializers.ModelSerializer
):
    voucher_no = serializers.CharField(required=False)
    status = serializers.ChoiceField(
        choices=JournalVoucher.STATUSES, default="Approved"
    )
    rows = PublicJournalVoucherRowSerializer(many=True)

    def validate(self, attrs):
        dr_total = Decimal(0)
        cr_total = Decimal(0)

        for row in attrs.get("rows"):
            dr_amt = row.get("dr_amount")
            cr_amt = row.get("cr_amount")
            account_id = row.get("account_id") or (row.get("account") and row["account"].get("id"))
            
            if not account_id:
                accounts = Account.objects.filter(**row.get("account"), company_id=self.context["request"].company_id)
                count = accounts.count()
                if count > 1:
                    raise ValidationError({"detail": "More than one account found for the given details."})
                elif count == 0:
                    raise ValidationError({"detail": "No account found for the given details."})
                else:
                    account_id = accounts.first().id
                    row["account_id"] = account_id
            
            if not dr_amt and not cr_amt:
                raise ValidationError({"detail": "Both Dr and Cr amounts cannot be 0."})
            
            dr_total += decimalize(dr_amt) if dr_amt else 0
            cr_total += decimalize(cr_amt) if cr_amt else 0


        if dr_total != cr_total:
            raise ValidationError({"detail": "Debit and Credit totals do not match."})

        return super().validate(attrs)

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        validated_data["company_id"] = self.context["request"].company_id
        validated_data["voucher_no"] = get_next_voucher_no(
            JournalVoucher, self.context["request"].company_id
        )
        journal_voucher = JournalVoucher.objects.create(**validated_data)
        for _, row in enumerate(rows_data):
            row.pop("account")
            JournalVoucherRow.objects.create(journal_voucher=journal_voucher, **row)
        JournalVoucher.apply_transactions(journal_voucher)
        return journal_voucher

    class Meta:
        model = JournalVoucher
        exclude = ("company", "id")


class PublicJournalVoucherCreateResponseSerializer(serializers.Serializer):
    voucher_no = serializers.CharField()


class PublicJournalVoucherStatusChangeSerializer(serializers.Serializer):
    voucher_no = serializers.CharField(required=True)
    status = serializers.ChoiceField(choices=JournalVoucher.STATUSES, required=True)
