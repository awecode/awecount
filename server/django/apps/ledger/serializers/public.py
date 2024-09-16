from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.models.base import Account, Party
from apps.voucher.models import SalesVoucher, SalesVoucherRow
from apps.voucher.models.journal_vouchers import JournalVoucher, JournalVoucherRow
from apps.voucher.serializers.sales import SalesVoucherAccessSerializer
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
                raise ValidationError(
                    f"No account found for the given details. {str(row.get('account'))}"
                )
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
        fields = ("voucher_no", "date", "narration", "status", "rows")


class PublicJournalVoucherCreateResponseSerializer(serializers.Serializer):
    voucher_no = serializers.CharField()


class PublicJournalVoucherStatusChangeSerializer(
    serializers.ModelSerializer, DisableCancelEditMixin
):
    reason = serializers.CharField(required=False)

    class Meta:
        model = JournalVoucher
        fields = ("voucher_no", "status", "reason")


class PublicPartyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = (
            "id",
            "name",
        )


class RoyaltyLedgerInfo(serializers.Serializer):
    royalty_expense_account_id = serializers.IntegerField(required=True)
    royalty_rate = serializers.FloatField(required=True)
    tds_category_id = serializers.IntegerField(required=True)
    tds_rate = serializers.FloatField(required=True)
    party_tax_registration_number = serializers.CharField(required=True)
    party_name = serializers.CharField(required=True)

    royalty_expense_account = None
    party_payable_account = None
    party_royalty_tds_accout = None


class PublicSalesVoucherAccessSerializer(SalesVoucherAccessSerializer):
    royalty_ledger_info = RoyaltyLedgerInfo(required=False)

    @transaction.atomic
    def validate_royalty_ledger_info(self, royalty_ledger_info):
        try:
            royalty_ledger_info["royalty_expense_account"] = Account.objects.get(
                id=royalty_ledger_info["royalty_expense_account_id"],
                company_id=self.context["request"].company_id,
            )
        except Account.DoesNotExist:
            raise ValidationError("Royalty expense account not found.")

        try:
            party = Party.objects.get(
                tax_registration_number=royalty_ledger_info[
                    "party_tax_registration_number"
                ],
                company_id=self.context["request"].company_id,
            )
        except Party.DoesNotExist:
            party = Party(
                name=royalty_ledger_info["party_name"],
                tax_registration_number=royalty_ledger_info[
                    "party_tax_registration_number"
                ],
                company_id=self.context["request"].company_id,
            )
            party.save()
        except Party.MultipleObjectsReturned:
            raise ValidationError("Multiple parties found.")

        royalty_ledger_info["party_payable_account"] = party.supplier_account

        try:
            party_royalty_tds_accout = Account.objects.get(
                source=party.supplier_account,
                category_id=royalty_ledger_info["tds_category_id"],
                company_id=self.context["request"].company_id,
            )
        except Account.DoesNotExist:
            party_royalty_tds_accout = Account(
                name="Royalty TDS - " + party.name,
                source=party.supplier_account,
                category_id=royalty_ledger_info["tds_category_id"],
                company_id=self.context["request"].company_id,
            )
            party_royalty_tds_accout.save()
        except Account.MultipleObjectsReturned:
            raise ValidationError("Multiple party royalty TDS accounts found.")
        royalty_ledger_info["party_royalty_tds_accout"] = party_royalty_tds_accout
        return royalty_ledger_info

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        royalty_ledger_info = validated_data.pop("royalty_ledger_info", None)
        challans = validated_data.pop("challans", None)
        if challans:
            self.check_challans(challans, rows_data)
        request = self.context["request"]
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data["company_id"] = request.company_id
        validated_data["user_id"] = request.user.id
        self.validate_invoice_date(validated_data)
        if validated_data.get("due_date"):
            self.validate_due_date(validated_data["due_date"])
        instance = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            # if row.item.track_inventory:
            # TODO: Verify if id is required or not
            if row.get("id"):
                row.pop("id")
            SalesVoucherRow.objects.create(voucher=instance, **row)
        if challans:
            instance.challans.clear()
            instance.challans.add(*challans)
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(
            voucher_meta=meta, royalty_ledger_info=royalty_ledger_info
        )
        # TODO: synchronize with CBMS
        # instance.synchronize()
        return instance
