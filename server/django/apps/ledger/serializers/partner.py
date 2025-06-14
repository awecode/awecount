import datetime
from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.models.base import Account, Party
from apps.ledger.serializers import PartySerializer
from apps.voucher.models import SalesVoucherRow
from apps.voucher.models.journal_vouchers import JournalVoucher, JournalVoucherRow
from apps.voucher.serializers.partner import PartnerItemSelectSerializer
from apps.voucher.serializers.sales import (
    SalesVoucherCreateSerializer,
    SalesVoucherRowSerializer,
)
from awecount.libs import decimalize, get_next_voucher_no
from awecount.libs.serializers import (
    DisableCancelEditMixin,
    RoyaltyLedgerInfoSerializer,
)
from lib.drf.serializers import BaseModelSerializer


class PartnerAccountSerializer(serializers.Serializer):
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
    supplier_detail__tax_identification_number = serializers.IntegerField(
        required=False
    )
    customer_detail__name = serializers.CharField(required=False)
    customer_detail__email = serializers.EmailField(required=False)
    customer_detail__contact_no = serializers.CharField(required=False)
    customer_detail__tax_identification_number = serializers.IntegerField(
        required=False
    )


class PartnerJournalVoucherRowSerializer(BaseModelSerializer):
    account = PartnerAccountSerializer(default={})
    account_id = serializers.IntegerField(required=False)
    dr_amount = serializers.DecimalField(
        max_digits=None, decimal_places=None, required=False
    )
    cr_amount = serializers.DecimalField(
        max_digits=None, decimal_places=None, required=False
    )

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


class PartnerJournalVoucherCreateSerializer(
    DisableCancelEditMixin, BaseModelSerializer
):
    voucher_no = serializers.CharField(required=False)
    status = serializers.ChoiceField(
        choices=JournalVoucher.STATUSES, default="Approved"
    )
    rows = PartnerJournalVoucherRowSerializer(many=True)

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
                    **row.get("account"), company_id=self.context["request"].company.id
                )
                row["account_id"] = account.id
            except Account.DoesNotExist:
                raise ValidationError(
                    f"No account found for the given details. {str(row.get('account'))}"
                )
            except Account.MultipleObjectsReturned:
                raise ValidationError(
                    f"More than one account found for the given details. {str(row.get('account'))}"
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
        validated_data["company_id"] = self.context["request"].company.id
        validated_data["voucher_no"] = get_next_voucher_no(
            JournalVoucher, self.context["request"].company.id
        )
        journal_voucher = JournalVoucher.objects.create(**validated_data)
        for _, row in enumerate(rows_data):
            row.pop("account")
            JournalVoucherRow.objects.create(journal_voucher=journal_voucher, **row)
        JournalVoucher.apply_transactions(journal_voucher)
        return journal_voucher

    class Meta:
        model = JournalVoucher
        fields = ("voucher_no", "date", "narration", "status", "rows")


class PartnerJournalVoucherCreateResponseSerializer(serializers.Serializer):
    voucher_no = serializers.CharField()


class PartnerJournalVoucherStatusChangeSerializer(
    BaseModelSerializer, DisableCancelEditMixin
):
    reason = serializers.CharField(required=False)

    class Meta:
        model = JournalVoucher
        fields = ("voucher_no", "status", "reason")


class PartnerPartyListSerializer(BaseModelSerializer):
    class Meta:
        model = Party
        fields = (
            "id",
            "name",
        )


class SalesVoucherRowAccessSerializer(
    PartnerItemSelectSerializer, SalesVoucherRowSerializer
):
    class Meta:
        model = SalesVoucherRow
        exclude = ("tax_scheme", "voucher", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class PartnerSalesVoucherCreateSerializer(SalesVoucherCreateSerializer):
    party_obj = PartySerializer(required=False)

    def validate(self, attrs):
        if not attrs.get("party") and attrs.get("party_obj"):
            party_obj = attrs.pop("party_obj")
            try:
                party = Party.objects.get(
                    **party_obj,
                    company_id=self.context["request"].company.id,
                )
            except Party.MultipleObjectsReturned:
                raise ValidationError("Multiple parties found for the given details.")
            except Party.DoesNotExist:
                party = Party.objects.create(
                    **party_obj,
                    company_id=self.context["request"].company.id,
                )

            attrs["party"] = party
        return super().validate(attrs)


class PartnerSalesVoucherAccessSerializer(
    PartnerSalesVoucherCreateSerializer, RoyaltyLedgerInfoSerializer
):
    """
    {"mode":"Cash","customer_name":"","status":"Issued","address":"ASD","discount_type":null,"discount":0,"is_export":false,"date":"2019-11-07","due_date":"2019-11-07","rows":[{"quantity":1,"discount":0,"discount_type":null,"trade_discount":false,"item_id":401,"tax_scheme_id":45,"rate":500,"unit_id":25,"description":""}],"trade_discount":true}

    """

    date = serializers.DateField(default=datetime.datetime.today().date)
    rows = SalesVoucherRowAccessSerializer(many=True)
    pdf_url = serializers.ReadOnlyField()
    view_url = serializers.ReadOnlyField()

    def create(self, validated_data):
        royalty_ledger_info = validated_data.pop("royalty_ledger_info", None)
        if royalty_ledger_info:
            extra_entries = []
            for party in royalty_ledger_info["parties"]:
                extra_entries.append(
                    [
                        "dr",
                        royalty_ledger_info["royalty_expense_account"],
                        party["royalty_amount"],
                    ]
                )
                extra_entries.append(
                    ["cr", party["royalty_tds_account"], party["tds_amount"]]
                )
                extra_entries.append(
                    [
                        "cr",
                        party["payable_account"],
                        party["royalty_amount"] - party["tds_amount"],
                    ]
                )
            validated_data["extra_entries"] = extra_entries
        return super().create(validated_data)
