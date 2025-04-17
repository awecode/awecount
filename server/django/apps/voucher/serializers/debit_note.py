from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.product.serializers import ItemPurchaseSerializer
from apps.voucher.serializers import (
    PurchaseDiscountSerializer,
    PurchaseVoucherRowDetailSerializer,
)
from awecount.libs import get_next_voucher_no
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.exception import UnprocessableException
from awecount.libs.serializers import StatusReversionMixin
from lib.drf.serializers import BaseModelSerializer

from ..models import DebitNote, DebitNoteRow
from .mixins import DiscountObjectTypeSerializerMixin


class DebitNoteRowSerializer(DiscountObjectTypeSerializerMixin, BaseModelSerializer):
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
        model = DebitNoteRow
        exclude = ("item", "tax_scheme", "voucher", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class DebitNoteCreateSerializer(
    StatusReversionMixin,
    DiscountObjectTypeSerializerMixin,
    BaseModelSerializer,
):
    voucher_no = serializers.ReadOnlyField()
    rows = DebitNoteRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance=None):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Draft", "Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            DebitNote, self.context["request"].company.id
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
            if row.get("discount_type") == "":
                row["discount_type"] = None
            row_serializer = DebitNoteRowSerializer(data=row)
            if not row_serializer.is_valid():
                raise serializers.ValidationError(row_serializer.errors)
        return rows

    def cancel_purchase(self, instance, rows_data):
        purchase_vouchers = instance.invoices.all()
        for voucher in purchase_vouchers:
            purchase_rows = voucher.rows.all()
            for row in purchase_rows:
                row_data = next(
                    (item for item in rows_data if item["id"] == row.id), None
                )
                if not row_data:
                    continue
                debit_note_row = instance.rows.get(item_id=row_data["item_id"])
                # TODO: with Transaction-FIFO, how to handle this?
                # if row.remaining_quantity < row_data["quantity"] and not self.context[
                #     "request"
                # ].query_params.get("fifo_inconsistency"):
                #     raise UnprocessableException(
                #         detail="This action may cause inconsistency in fifo.",
                #         code="fifo_inconsistency",
                #     )
                # FIXME: The transcation has already been applied. Because of which the remaning quantity has already been deducted.
                if row_data["quantity"] > row.item.remaining_stock and not (
                    self.context["request"].query_params.get("negative_stock")
                    or self.context["request"].query_params.get("fifo_inconsistency")
                ):
                    raise UnprocessableException(
                        detail="This can cause inconsistency in fifo.",
                        code="negative_stock",
                    )
                    # TODO: with Transaction-FIFO, how to handle this?

                # if row.remaining_quantity < row_data["quantity"]:
                #     diff = row_data["quantity"] - row.remaining_quantity
                #     debit_note_row.purchase_row_data[
                #         str(row.id)
                #     ] = row.remaining_quantity
                #     row.remaining_quantity = 0
                #     row.save()
                #     available_rows = row.item.purchase_rows.filter(
                #         remaining_quantity__gt=0
                #     ).order_by("-voucher__date", "-id")
                #     for row in available_rows:
                #         if row.remaining_quantity > diff:
                #             debit_note_row.purchase_row_data[str(row.id)] = diff
                #             row.remaining_quantity -= diff
                #             row.save()
                #             break
                #         else:
                #             debit_note_row.purchase_row_data[
                #                 str(row.id)
                #             ] = row.remaining_quantity
                #             diff -= row.remaining_quantity
                #             row.remaining_quantity = 0
                #             row.save()
                #             continue
                # else:
                # row.remaining_quantity -= row_data["quantity"]
                # row.save()
                debit_note_row.purchase_row_data[str(row.id)] = row_data["quantity"]
                debit_note_row.save()

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        invoices = validated_data.pop("invoices")
        request = self.context["request"]
        self.assign_fiscal_year(validated_data)
        self.assign_voucher_number(validated_data)
        self.assign_discount_obj(validated_data)
        validated_data["company_id"] = request.company.id
        validated_data["user_id"] = request.user.id
        instance = DebitNote.objects.create(**validated_data)

        for index, row in enumerate(rows_data):
            row["purchase_row_data"] = {"id": row.pop("id")}
            row = self.assign_discount_obj(row)
            DebitNoteRow.objects.create(voucher=instance, **row)
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.apply_transactions()

        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        invoices = validated_data.pop("invoices")
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        DebitNote.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            DebitNoteRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.refresh_from_db()
        instance.apply_transactions()
        return instance

    class Meta:
        model = DebitNote
        exclude = (
            "company",
            "user",
            "bank_account",
            "discount_obj",
            "fiscal_year",
        )


class DebitNoteListSerializer(BaseModelSerializer):
    party = serializers.ReadOnlyField(source="party.name")

    class Meta:
        model = DebitNote
        fields = (
            "id",
            "voucher_no",
            "party",
            "date",
            "status",
        )


class DebitNoteRowDetailSerializer(PurchaseVoucherRowDetailSerializer):
    selected_item_obj = ItemPurchaseSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")


class DebitNoteDetailSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    discount_obj = PurchaseDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")
    address = serializers.ReadOnlyField(source="party.address")

    rows = DebitNoteRowDetailSerializer(many=True)
    tax_identification_number = serializers.ReadOnlyField(
        source="party.tax_identification_number"
    )

    invoice_data = serializers.SerializerMethodField()

    def get_invoice_data(self, obj):
        data = []
        for invoice in obj.invoices.all():
            data.append({"id": invoice.id, "voucher_no": invoice.voucher_no})
        return data

    class Meta:
        model = DebitNote
        exclude = ("company", "user", "bank_account")
