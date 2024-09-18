from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.product.models import Item
from apps.product.serializers import ItemSerializer
from apps.voucher.models import PurchaseVoucher, PurchaseVoucherRow
from apps.voucher.models.discounts import PurchaseDiscount
from apps.voucher.serializers.mixins import (
    DiscountObjectTypeSerializerMixin,
    ModeCumBankSerializerMixin,
)
from awecount.libs.exception import UnprocessableException
from awecount.libs.serializers import StatusReversionMixin


class PartnerItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
    voucher_no = serializers.CharField(required=False)
    selling_price = serializers.FloatField(required=False)
    cost_price = serializers.FloatField(required=False)
    sales_account_type = serializers.CharField(required=False)
    purchase_account_type = serializers.CharField(required=False)
    discount_allowed_account_type = serializers.CharField(required=False)
    discount_received_account_type = serializers.CharField(required=False)
    track_inventory = serializers.BooleanField(required=False)
    can_be_sold = serializers.BooleanField(required=False)
    can_be_purchased = serializers.BooleanField(required=False)
    fixed_asset = serializers.BooleanField(required=False)
    direct_expense = serializers.BooleanField(required=False)
    indirect_expense = serializers.BooleanField(required=False)

    category__id = serializers.IntegerField(required=False)
    category__name = serializers.CharField(required=False)

    brand__id = serializers.IntegerField(required=False)
    brand__name = serializers.CharField(required=False)

    tax_scheme__id = serializers.IntegerField(required=False)
    tax_scheme__name = serializers.CharField(required=False)

    account__id = serializers.IntegerField(required=False)
    account__name = serializers.CharField(required=False)
    account__code = serializers.CharField(required=False)
    account__account_no = serializers.CharField(required=False)

    sales_account__id = serializers.IntegerField(required=False)
    sales_account__name = serializers.CharField(required=False)
    sales_account__code = serializers.CharField(required=False)

    dedicated_sales_account__id = serializers.IntegerField(required=False)
    dedicated_sales_account__name = serializers.CharField(required=False)
    dedicated_sales_account__code = serializers.CharField(required=False)

    purchase_account__id = serializers.IntegerField(required=False)
    purchase_account__name = serializers.CharField(required=False)
    purchase_account__code = serializers.CharField(required=False)

    dedicated_purchase_account__id = serializers.IntegerField(required=False)
    dedicated_purchase_account__name = serializers.CharField(required=False)
    dedicated_purchase_account__code = serializers.CharField(required=False)

    discount_allowed_account__id = serializers.IntegerField(required=False)
    discount_allowed_account__name = serializers.CharField(required=False)
    discount_allowed_account__code = serializers.CharField(required=False)

    dedicated_discount_allowed_account__id = serializers.IntegerField(required=False)
    dedicated_discount_allowed_account__name = serializers.CharField(required=False)
    dedicated_discount_allowed_account__code = serializers.CharField(required=False)

    discount_received_account__id = serializers.IntegerField(required=False)
    discount_received_account__name = serializers.CharField(required=False)
    discount_received_account__code = serializers.CharField(required=False)

    dedicated_discount_received_account__id = serializers.IntegerField(required=False)
    dedicated_discount_received_account__name = serializers.CharField(required=False)
    dedicated_discount_received_account__code = serializers.CharField(required=False)

    expense_account__id = serializers.IntegerField(required=False)
    expense_account__name = serializers.CharField(required=False)
    expense_account__code = serializers.CharField(required=False)

    fixed_asset_account__id = serializers.IntegerField(required=False)
    fixed_asset_account__name = serializers.CharField(required=False)
    fixed_asset_account__code = serializers.CharField(required=False)


class ItemCreateSerializer(ItemSerializer):
    pass


class PartnerPurchaseVoucherRowSerializer(
    DiscountObjectTypeSerializerMixin, serializers.ModelSerializer
):
    id = serializers.IntegerField(required=False)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)
    item = serializers.ReadOnlyField(source="item.name")
    buyers_name = serializers.ReadOnlyField(source="voucher.buyer_name")
    voucher__date = serializers.ReadOnlyField(source="voucher.date")
    voucher__voucher_no = serializers.ReadOnlyField(source="voucher.voucher_no")
    voucher_id = serializers.ReadOnlyField(source="voucher.id")

    item_id = serializers.IntegerField(required=False)
    item = PartnerItemSerializer(default={})
    item_obj = ItemCreateSerializer(required=False, allow_null=True)

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


class PartnerPurchaseVoucherCreateSerializer(
    StatusReversionMixin,
    DiscountObjectTypeSerializerMixin,
    ModeCumBankSerializerMixin,
    serializers.ModelSerializer,
):
    rows = PartnerPurchaseVoucherRowSerializer(many=True)
    purchase_order_numbers = serializers.ReadOnlyField()

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
        company = self.context["request"].company

        if (
            not data.get("party")
            and data.get("mode") == "Credit"
            and data.get("status") != "Draft"
        ):
            raise ValidationError(
                {"party": ["Party is required for a credit issue."]},
            )
        request = self.context["request"]

        if data.get("discount") and data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})

        if request.query_params.get("fifo_inconsistency"):
            return data
        else:
            if request.company.inventory_setting.enable_fifo:
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
                return data

        party = data.get("party")
        fiscal_year = self.context["request"].company.current_fiscal_year
        voucher_no = data.get("voucher_no")

        if not company.purchase_setting.enable_empty_voucher_no:
            if not voucher_no:
                raise ValidationError({"voucher_no": ["This field cannot be empty."]})
            if self.Meta.model.objects.filter(
                voucher_no=voucher_no, party=party, fiscal_year=fiscal_year
            ).exists():
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
        for row in rows:
            item_obj = row.pop("item_obj")

            item_id = row.get("item_id")
            if item_id:
                row["item"]["id"] = item_id

            try:
                item = Item.objects.get(
                    **row.get("item"), company_id=self.context["request"].company_id
                )
                if item_obj:
                    if item_obj.get("name"):
                        item.name = item_obj.get("name")
                    if item_obj.get("cost_price"):
                        item.cost_price = item_obj.get("cost_price")
                    item.save()

                row["item_id"] = item.id
            except Item.DoesNotExist:
                if item_obj is None:
                    raise ValidationError(
                        "No item found for the given details. " + str(row.get("item"))
                    )
                category = item_obj.get("category")
                new_item = Item(
                    company_id=self.context["request"].company_id,
                    **item_obj,
                    sales_account_type=category.items_sales_account_type,
                    sales_account=category.dedicated_sales_account,
                    purchase_account_type=category.items_purchase_account_type,
                    purchase_account=category.dedicated_purchase_account,
                    discount_allowed_account_type=category.items_discount_allowed_account_type,
                    discount_allowed_account=category.dedicated_discount_allowed_account,
                    discount_received_account_type=category.items_discount_received_account_type,
                    discount_received_account=category.dedicated_discount_received_account,
                )
                new_item.save()
                row["item_id"] = new_item.id

            except Item.MultipleObjectsReturned:
                raise ValidationError(
                    "More than one item found for the given details. "
                    + str(row.get("item"))
                )

            if row.get("discount_type") == "":
                row["discount_type"] = None
            row_serializer = PartnerPurchaseVoucherRowSerializer(data=row)
            if not row_serializer.is_valid():
                raise serializers.ValidationError(row_serializer.errors)
        return rows

    # def validate_discount_type(self, attr):
    #     if not attr:
    #         attr = 0
    #     return attr

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        if validated_data.get("voucher_no") == "":
            validated_data["voucher_no"] = None
        request = self.context["request"]
        purchase_orders = validated_data.pop("purchase_orders", None)
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data["company_id"] = request.company_id
        validated_data["user_id"] = request.user.id
        instance = PurchaseVoucher.objects.create(**validated_data)
        for _, row in enumerate(rows_data):
            row.pop("item")
            row = self.assign_discount_obj(row)
            PurchaseVoucherRow.objects.create(voucher=instance, **row)
        if purchase_orders:
            instance.purchase_orders.clear()
            instance.purchase_orders.set(purchase_orders)
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(voucher_meta=meta)
        return instance

    class Meta:
        model = PurchaseVoucher
        exclude = ("company", "user", "bank_account", "discount_obj", "fiscal_year")


class PartnerPurchaseDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDiscount
        exclude = ("company",)
        extra_kwargs = {"name": {"required": True}}
