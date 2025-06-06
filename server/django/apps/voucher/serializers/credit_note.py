from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from awecount.libs import get_next_voucher_no
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.serializers import StatusReversionMixin
from lib.drf.serializers import BaseModelSerializer

from ..models import CreditNote, CreditNoteRow
from .mixins import DiscountObjectTypeSerializerMixin
from .sales import (
    ItemSalesSerializer,
    SalesDiscountSerializer,
    SalesVoucherRowDetailSerializer,
)


class CreditNoteRowSerializer(DiscountObjectTypeSerializerMixin, BaseModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_discount(self, value):
        if not value:
            value = 0
        elif value < 0:
            raise serializers.ValidationError("Discount can't be negative.")
        return value

    class Meta:
        model = CreditNoteRow
        exclude = ("item", "tax_scheme", "voucher", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class CreditNoteCreateSerializer(
    StatusReversionMixin,
    DiscountObjectTypeSerializerMixin,
    BaseModelSerializer,
):
    voucher_no = serializers.ReadOnlyField()
    rows = CreditNoteRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance=None):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Draft", "Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            CreditNote, self.context["request"].company.id
        )
        validated_data["voucher_no"] = next_voucher_no

    def assign_fiscal_year(self, validated_data, instance=None):
        if instance and instance.fiscal_year_id:
            return
        fiscal_year = self.context["request"].company.current_fiscal_year
        if fiscal_year.includes(validated_data.get("date")):
            validated_data["fiscal_year_id"] = fiscal_year.id
        else:
            raise ValidationError(
                {"date": ["Date not in current fiscal year."]},
            )

    def validate(self, data):
        if (
            not data.get("party")
            and not data.get("payment_mode")
            and data.get("status") != "Draft"
        ):
            raise ValidationError(
                {"party": ["Party is required for a credit issue."]},
            )
        if data.get("discount") and data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})
        return data

    def validate_rows(self, rows):
        for row in rows:
            # if row.get("discount_type") == "":
            #     row["discount_type"] = None
            row_serializer = CreditNoteRowSerializer(data=row)
            if not row_serializer.is_valid():
                raise serializers.ValidationError(row_serializer.errors)
        return rows

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        invoices = validated_data.pop("invoices")
        extra_entries = validated_data.pop("extra_entries", None)
        request = self.context["request"]
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        validated_data["company_id"] = request.company.id
        validated_data["user_id"] = request.user.id
        instance = CreditNote.objects.create(**validated_data)
        # sales_row_ids = []
        # FIXME: Why enumerate?
        for index, row in enumerate(rows_data):
            row["sales_row_data"] = {"id": row.pop("id")}
            row = self.assign_discount_obj(row)
            CreditNoteRow.objects.create(voucher=instance, **row)
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.apply_transactions(extra_entries=extra_entries)
        # instance.synchronize()
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        invoices = validated_data.pop("invoices")
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        CreditNote.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            CreditNoteRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.refresh_from_db()
        instance.apply_transactions()
        # instance.synchronize()
        return instance

    class Meta:
        model = CreditNote
        exclude = (
            "company",
            "user",
            "bank_account",
            "discount_obj",
            "fiscal_year",
        )


class CreditNoteListSerializer(BaseModelSerializer):
    party = serializers.ReadOnlyField(source="party.name")

    class Meta:
        model = CreditNote
        fields = (
            "id",
            "voucher_no",
            "party",
            "date",
            "status",
        )


class CreditNoteRowDetailSerializer(SalesVoucherRowDetailSerializer):
    selected_item_obj = ItemSalesSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")


class CreditNoteDetailSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    discount_obj = SalesDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")
    address = serializers.ReadOnlyField(source="party.address")

    rows = CreditNoteRowDetailSerializer(many=True)
    tax_identification_number = serializers.ReadOnlyField(
        source="party.tax_identification_number"
    )

    invoice_data = serializers.SerializerMethodField()
    # invoices = serializers.SerializerMethodField()

    # def get_invoices(self, obj):
    #     return obj.invoices.values_list("id", flat=True)

    def get_invoice_data(self, obj):
        data = []
        for invoice in obj.invoices.all():
            data.append({"id": invoice.id, "voucher_no": invoice.voucher_no})
        return data

    class Meta:
        model = CreditNote
        exclude = ("company", "user", "bank_account")
