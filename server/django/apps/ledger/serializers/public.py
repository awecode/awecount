from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.models.base import Account
from apps.voucher.models.journal_vouchers import JournalVoucher, JournalVoucherRow
from awecount.libs import decimalize, get_next_voucher_no
from awecount.libs.serializers import DisableCancelEditMixin


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
        fields = (
            "type",
            "description",
            "dr_amount",
            "cr_amount",
            "account",
            "account_id",
        )


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

            account_id = row.get("account_id")
            if account_id:
                row["account"]["id"] = account_id

            try:
                account = Account.objects.get(
                    **row.get("account"), company_id=self.context["request"].company_id
                )
                row["account_id"] = account.id
            except Account.DoesNotExist:
                raise ValidationError("No account found for the given details.")
            except Account.MultipleObjectsReturned:
                raise ValidationError(
                    "More than one account found for the given details."
                )

            if not dr_amt and not cr_amt:
                raise ValidationError("Both Dr and Cr amounts can not be empty.")

            dr_total += decimalize(dr_amt) if dr_amt else 0
            cr_total += decimalize(cr_amt) if cr_amt else 0

        if dr_total != cr_total:
            raise ValidationError("Debit and credit totals do not match.")

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


class PublicJournalVoucherStatusChangeSerializer(
    serializers.ModelSerializer, DisableCancelEditMixin
):
    class Meta:
        model = JournalVoucher
        fields = ("voucher_no", "status")
