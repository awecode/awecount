from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.serializers import PartyMinSerializer
from apps.product.models import Item
from apps.product.serializers import ItemPurchaseSerializer
from apps.tax.serializers import TaxSchemeSerializer
from awecount.libs import get_next_voucher_no
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.exception import UnprocessableException
from awecount.libs.serializers import StatusReversionMixin
from lib.drf.serializers import BaseModelSerializer

from ..models import (
    LandedCostRow,
    PurchaseDiscount,
    PurchaseOrder,
    PurchaseOrderRow,
    PurchaseVoucher,
    PurchaseVoucherRow,
)
from .landed_cost import LandedCostRowSerializer
from .mixins import DiscountObjectTypeSerializerMixin


class PurchaseDiscountSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseDiscount
        exclude = ("company",)
        extra_kwargs = {"name": {"required": True}}


class PurchaseVoucherRowSerializer(
    DiscountObjectTypeSerializerMixin, BaseModelSerializer
):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)
    item = serializers.ReadOnlyField(source="item.name")
    buyers_name = serializers.ReadOnlyField(source="voucher.buyer_name")
    voucher__date = serializers.ReadOnlyField(source="voucher.date")
    voucher__voucher_no = serializers.ReadOnlyField(source="voucher.voucher_no")
    voucher_id = serializers.ReadOnlyField(source="voucher.id")
    selected_item_obj = ItemPurchaseSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")

    def validate_discount(self, value):
        if not value:
            value = 0
        elif value < 0:
            raise serializers.ValidationError("Discount can't be negative.")
        return value

    class Meta:
        model = PurchaseVoucherRow
        exclude = ("tax_scheme", "voucher", "unit", "discount_obj")

        extra_kwargs = {
            "discount": {"required": False, "allow_null": True},
            "discount_type": {"allow_null": True, "required": False},
        }


class PurchaseVoucherCreateSerializer(
    StatusReversionMixin,
    DiscountObjectTypeSerializerMixin,
    BaseModelSerializer,
):
    rows = PurchaseVoucherRowSerializer(many=True)
    landed_cost_rows = LandedCostRowSerializer(many=True, required=False)
    purchase_order_numbers = serializers.ReadOnlyField()
    selected_party_obj = PartyMinSerializer(source="party", read_only=True)
    selected_mode_obj = GenericSerializer(source="bank_account", read_only=True)

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
        request = self.context["request"]
        company = request.company

        party = data.get("party")
        if not party and not data.get("payment_mode") and data.get("status") != "Draft":
            raise ValidationError(
                {"party": ["Party is required for a credit issue."]},
            )

        if data.get("discount") and data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})

        # FIFO inconsistency check
        if company.inventory_setting.enable_fifo and not request.query_params.get(
            "fifo_inconsistency"
        ):
            item_ids = [x.get("item_id") for x in data.get("rows")]
            date = data["date"]
            if PurchaseVoucherRow.objects.filter(
                voucher__date__gt=date,
                item__in=item_ids,
                item__track_inventory=True,
            ).exists():
                raise UnprocessableException(
                    detail="Creating a purchase on a past date when purchase for the same item on later dates exist may cause inconsistencies in FIFO.",
                    code="fifo_inconsistency",
                )

        fiscal_year = self.context["request"].company.current_fiscal_year
        voucher_no = data.get("voucher_no")

        if not company.purchase_setting.enable_empty_voucher_no:
            if not voucher_no:
                raise ValidationError({"voucher_no": ["This field cannot be empty."]})

            qs = self.Meta.model.objects.filter(
                voucher_no=voucher_no, party=party, fiscal_year=fiscal_year
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    {
                        "voucher_no": [
                            "Purchase with the bill number for the chosen party already exists."
                        ]
                    }
                )

        if data.get("discount") and data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})

        return data

        # if request.query_params.get("fifo_inconsistency"):
        #     return data
        # else:#
        #     if request.company.inventory_setting.enable_fifo:
        #         item_ids = [x.get("item_id") for x in data.get("rows")]
        #         date = data["date"]
        #         if PurchaseVoucherRow.objects.filter(voucher__date__gt=date, item__in=item_ids, item__track_inventory=True).exists():
        #             raise UnprocessableException(detail="Creating a purchase on a past date when purchase for the same item on later dates exist may cause inconsistencies in FIFO.", code="fifo_inconsistency")
        #     return data

    def validate_rows(self, rows):
        request = self.context["request"]
        purchase_setting = request.company.purchase_setting

        # Collect all item IDs and fetch items in a single query
        item_ids = [row.get("item_id") for row in rows]
        items = {item.id: item for item in Item.objects.filter(id__in=item_ids)}

        for row in rows:
            item_id = row.get("item_id")
            item = items.get(item_id)
            if not item:
                raise serializers.ValidationError({"item_id": ["Item not found."]})

            if row.get("discount_type") == "":
                row["discount_type"] = None
            row_serializer = PurchaseVoucherRowSerializer(
                data=row, context=self.context
            )
            if not row_serializer.is_valid():
                raise serializers.ValidationError(row_serializer.errors)
        return rows

    # def validate_discount_type(self, attr):
    #     if not attr:
    #         attr = 0
    #     return attr

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        landed_cost_rows_data = validated_data.pop("landed_cost_rows", [])
        if validated_data.get("voucher_no") == "":
            validated_data["voucher_no"] = None
        request = self.context["request"]
        purchase_orders = validated_data.pop("purchase_orders", None)
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        validated_data["company_id"] = request.company.id
        validated_data["user_id"] = request.user.id
        instance = PurchaseVoucher.objects.create(**validated_data)

        # Create purchase voucher rows
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            PurchaseVoucherRow.objects.create(voucher=instance, **row)

        # Create landed cost if rows exist
        for row_data in landed_cost_rows_data:
            LandedCostRow.objects.create(invoice=instance, **row_data)

        if purchase_orders:
            instance.purchase_orders.clear()
            instance.purchase_orders.set(purchase_orders)
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(voucher_meta=meta)
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        landed_cost_rows_data = validated_data.pop("landed_cost_rows", [])
        if validated_data.get("voucher_no") == "":
            validated_data["voucher_no"] = None
        purchase_orders = validated_data.pop("purchase_orders", None)
        self.assign_fiscal_year(validated_data, instance=instance)
        self.assign_discount_obj(validated_data)
        PurchaseVoucher.objects.filter(pk=instance.id).update(**validated_data)

        # Update purchase voucher rows
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            PurchaseVoucherRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )

        # Update landed cost rows
        if landed_cost_rows_data:
            # Delete existing rows
            instance.landed_cost_rows.all().delete()
            # Create new rows
            for row_data in landed_cost_rows_data:
                LandedCostRow.objects.create(invoice=instance, **row_data)

        if purchase_orders:
            instance.purchase_orders.clear()
            instance.purchase_orders.set(purchase_orders)
        instance.refresh_from_db()
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(voucher_meta=meta)
        return instance

    class Meta:
        model = PurchaseVoucher
        exclude = ("company", "user", "bank_account", "discount_obj", "fiscal_year")


class PurchaseVoucherListSerializer(BaseModelSerializer):
    party = serializers.ReadOnlyField(source="party.name")
    name = serializers.SerializerMethodField()
    payment_mode = serializers.SerializerMethodField()

    def get_name(self, obj):
        return "{}".format(obj.voucher_no)

    def get_payment_mode(self, obj):
        if not obj.payment_mode:
            return "Credit"
        return obj.payment_mode.name

    class Meta:
        model = PurchaseVoucher
        fields = (
            "id",
            "voucher_no",
            "party",
            "date",
            "name",
            "status",
            "total_amount",
            "payment_mode",
        )


class PurchaseVoucherRowDetailSerializer(BaseModelSerializer):
    item_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField()
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")
    discount_obj = PurchaseDiscountSerializer()
    tax_scheme = TaxSchemeSerializer()
    hs_code = serializers.ReadOnlyField(source="item.category.hs_code")
    selected_item_obj = ItemPurchaseSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")

    class Meta:
        model = PurchaseVoucherRow
        exclude = ("voucher", "item", "unit")


class PurchaseVoucherDetailSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    discount_obj = PurchaseDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")
    landed_cost_rows = LandedCostRowSerializer(many=True, read_only=True)

    rows = PurchaseVoucherRowDetailSerializer(many=True)
    tax_identification_number = serializers.ReadOnlyField(
        source="party.tax_identification_number"
    )
    enable_row_description = serializers.ReadOnlyField(
        source="company.purchase_setting.enable_row_description"
    )
    purchase_order_numbers = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseVoucher
        exclude = (
            "company",
            "user",
            "bank_account",
        )


class PurchaseBookExportSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    tax_identification_number = serializers.ReadOnlyField(
        source="party.tax_identification_number"
    )
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")

    class Meta:
        model = PurchaseVoucher
        fields = (
            "date",
            "party_name",
            "tax_identification_number",
            "voucher_no",
            "voucher_meta",
        )


class PurchaseOrderRowSerializer(BaseModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    unit_id = serializers.IntegerField(required=False)
    selected_item_obj = ItemPurchaseSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")

    class Meta:
        model = PurchaseOrderRow
        exclude = ["item", "voucher", "unit"]


class PurchaseOrderListSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")

    class Meta:
        model = PurchaseOrder
        fields = ["id", "voucher_no", "party_name", "date", "status"]


class PurchaseOrderCreateSerializer(BaseModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    print_count = serializers.ReadOnlyField()
    rows = PurchaseOrderRowSerializer(many=True)
    selected_party_obj = GenericSerializer(read_only=True, source="party")

    class Meta:
        model = PurchaseOrder
        exclude = ["company", "user"]
        extra_kwargs = {"fiscal_year": {"read_only": True}}

    def assign_fiscal_year(self, validated_data, instance=None):
        if instance and instance.fiscal_year_id:
            return
        fiscal_year = self.context["request"].company.current_fiscal_year
        if fiscal_year.includes(validated_data.get("date")):
            validated_data["fiscal_year_id"] = fiscal_year.id
        else:
            raise ValidationError({"date": ["Date not in current fiscal year."]})

    def assign_voucher_number(self, validated_data, instance=None):
        if instance and instance.voucher_no:
            return
        next_voucher_no = get_next_voucher_no(
            PurchaseOrder, self.context["request"].company.id
        )
        validated_data["voucher_no"] = next_voucher_no

    def validate_party(self, attr):
        if not attr:
            raise ValidationError("You must select a party.")
        return attr

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        request = self.context["request"]
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        validated_data["company_id"] = request.company.id
        validated_data["user_id"] = request.user.id
        instance = PurchaseOrder.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            PurchaseOrderRow.objects.create(voucher=instance, **row)
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_fiscal_year(validated_data, instance=instance)
        # self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.Meta.model.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            PurchaseOrderRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
        return instance
