from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.product.models import Item
from apps.product.serializers import ItemPurchaseSerializer, ItemSerializer
from apps.voucher.models import (
    CreditNoteRow,
    DebitNoteRow,
    PaymentMode,
    PurchaseVoucher,
    PurchaseVoucherRow,
)
from apps.voucher.models.discounts import PurchaseDiscount
from apps.voucher.serializers.credit_note import (
    CreditNoteCreateSerializer,
    CreditNoteRowSerializer,
)
from apps.voucher.serializers.debit_note import (
    DebitNoteCreateSerializer,
    DebitNoteRowSerializer,
)
from apps.voucher.serializers.mixins import (
    DiscountObjectTypeSerializerMixin,
)
from awecount.libs.exception import UnprocessableException
from awecount.libs.serializers import (
    RoyaltyLedgerInfoSerializer,
    StatusReversionMixin,
)
from lib.drf.serializers import BaseModelSerializer


class PartnerItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
    voucher_no = serializers.CharField(required=False)
    selling_price = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        required=False,
    )
    cost_price = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        required=False,
    )
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


class PartnerItemSelectSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=False)
    item_obj = PartnerItemSerializer(default={})
    item = ItemCreateSerializer(required=False, write_only=True)

    def validate(self, attrs):
        item_obj = attrs.pop("item_obj")
        row_item = attrs.get("item")

        item_id = attrs.get("item_id")
        if item_id:
            item_obj["id"] = item_id

        try:
            item = Item.objects.get(
                **item_obj, company_id=self.context["request"].company.id
            )
            if row_item:
                if row_item.get("name"):
                    item.name = row_item.get("name")
                if row_item.get("cost_price"):
                    item.cost_price = row_item.get("cost_price")
                item.save()

        except Item.DoesNotExist:
            if row_item is None:
                raise ValidationError(
                    "No item found for the given details. " + str(item_obj)
                )
            item = Item(
                company_id=self.context["request"].company.id,
                **row_item,
            )
            category = row_item.get("category")
            if category:
                if category.sales_account:
                    item.sales_account_type = "category"
                    item.sales_account = category.dedicated_sales_account
                if category.purchase_account:
                    item.purchase_account_type = "category"
                    item.purchase_account = category.dedicated_purchase_account
                if category.discount_allowed_account:
                    item.discount_allowed_account_type = "category"
                    item.discount_allowed_account = (
                        category.dedicated_discount_allowed_account
                    )
                if category.discount_received_account:
                    item.discount_received_account_type = "category"
                    item.discount_received_account = (
                        category.dedicated_discount_received_account
                    )
            item.save()

        except Item.MultipleObjectsReturned:
            raise ValidationError(
                "More than one item found for the given details. " + str(item_obj)
            )

        attrs["item_id"] = item.id
        attrs["item"] = item

        return attrs


class PartnerPurchaseVoucherRowSerializer(
    DiscountObjectTypeSerializerMixin,
    BaseModelSerializer,
    PartnerItemSelectSerializer,
):
    id = serializers.IntegerField(required=False)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)
    item__account__current_balance = serializers.ReadOnlyField(
        source="item.account.current_balance"
    )
    buyers_name = serializers.ReadOnlyField(source="voucher.buyer_name")
    voucher__date = serializers.ReadOnlyField(source="voucher.date")
    voucher__voucher_no = serializers.ReadOnlyField(source="voucher.voucher_no")
    voucher_id = serializers.ReadOnlyField(source="voucher.id")
    selected_item_obj = ItemPurchaseSerializer(read_only=True, source="item")

    def validate_discount_type(self, value):
        if value == "":
            return None
        return value

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
    BaseModelSerializer,
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
            and not data.get("payment_mode")
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
            if not voucher_no and data.get("status") != "Draft":
                raise ValidationError({"voucher_no": ["This field cannot be empty."]})
            if (
                voucher_no
                and self.Meta.model.objects.filter(
                    voucher_no=voucher_no, party=party, fiscal_year=fiscal_year
                ).exists()
            ):
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

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        if validated_data.get("voucher_no") == "":
            validated_data["voucher_no"] = None
        request = self.context["request"]
        purchase_orders = validated_data.pop("purchase_orders", None)
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        validated_data["company_id"] = request.company.id
        validated_data["user_id"] = request.user.id
        instance = PurchaseVoucher.objects.create(**validated_data)
        for _, row in enumerate(rows_data):
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


class PartnerPurchaseVoucherListSerializer(BaseModelSerializer):
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


class PartnerPurchaseDiscountSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseDiscount
        exclude = ("company",)
        extra_kwargs = {"name": {"required": True}}


class PartnerCreditNoteRowSerializer(
    PartnerItemSelectSerializer, CreditNoteRowSerializer
):
    class Meta:
        model = CreditNoteRow
        exclude = ("tax_scheme", "voucher", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class PartnerCreditNoteCreateSerializer(
    CreditNoteCreateSerializer, RoyaltyLedgerInfoSerializer
):
    rows = PartnerCreditNoteRowSerializer(many=True)

    def create(self, validated_data):
        royalty_ledger_info = validated_data.pop("royalty_ledger_info", None)
        if royalty_ledger_info:
            extra_entries = []
            for party in royalty_ledger_info["parties"]:
                extra_entries.append(
                    [
                        "cr",
                        royalty_ledger_info["royalty_expense_account"],
                        party["royalty_amount"],
                    ]
                )
                extra_entries.append(
                    ["dr", party["royalty_tds_account"], party["tds_amount"]]
                )
                extra_entries.append(
                    [
                        "dr",
                        party["payable_account"],
                        party["royalty_amount"] - party["tds_amount"],
                    ]
                )
            validated_data["extra_entries"] = extra_entries
        return super().create(validated_data)


class PartnerDebitNoteRowSerializer(
    PartnerItemSelectSerializer, DebitNoteRowSerializer
):
    class Meta:
        model = DebitNoteRow
        exclude = ("tax_scheme", "voucher", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class PartnerDebitNoteCreateSerializer(DebitNoteCreateSerializer):
    rows = PartnerDebitNoteRowSerializer(many=True)


class PartnerPaymentModeSerializer(BaseModelSerializer):
    class Meta:
        model = PaymentMode
        fields = [
            "id",
            "name",
        ]
