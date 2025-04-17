import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import F, Q
from rest_framework import serializers

from apps.ledger.models import Account
from apps.ledger.serializers import AccountBalanceSerializer, AccountMinSerializer
from apps.product.helpers import create_book_category
from apps.product.models import Item, Transaction
from apps.tax.serializers import TaxSchemeSerializer
from awecount.libs import get_next_voucher_no
from awecount.libs.Base64FileField import Base64FileField
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.exception import UnprocessableException
from lib.drf.serializers import BaseModelSerializer

from ..models import (
    BillOfMaterial,
    BillOfMaterialRow,
    Brand,
    Category,
    InventoryAccount,
    InventoryAdjustmentVoucher,
    InventoryAdjustmentVoucherRow,
    InventoryConversionVoucher,
    InventoryConversionVoucherRow,
    InventorySetting,
    JournalEntry,
    Unit,
)
from ..models import (
    Category as InventoryCategory,
)


class ItemSerializer(BaseModelSerializer):
    tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    unit_id = serializers.IntegerField(required=False, allow_null=True)
    default_unit_obj = GenericSerializer(read_only=True, source="unit")
    default_tax_scheme_obj = GenericSerializer(read_only=True, source="tax_scheme")
    extra_fields = serializers.ReadOnlyField(source="category.extra_fields")
    front_image = Base64FileField(required=False, allow_null=True)
    back_image = Base64FileField(required=False, allow_null=True)

    def validate_cost_price(self, attr):
        if attr and attr < 0:
            raise ValidationError("Cost price cannot be negative.")
        return attr

    def validate_selling_price(self, attr):
        if attr and attr < 0:
            raise ValidationError("Selling price cannot be negative.")
        return attr

    def validate(self, attrs):
        if attrs.get("direct_expenses") and attrs.get("indirect_expenses"):
            raise ValidationError(
                "Item cannot be both direct and indirect expense at the same time."
            )
        # if (
        #     attrs.get("purchase_account_type") == "Category"
        #     or attrs.get("sales_account_type") == "Category"
        #     or attrs.get("discount_received_account_type") == "Category"
        #     or attrs.get("discount_allowed_account_type") == "Category"
        # ) and not attrs.get("category"):
        #     raise serializers.ValidationError(
        #         {"category": ["Category must be selected to use category account."]}
        #     )

        type_account_tuples = [
            ("sales_account_type", "sales_account"),
            ("purchase_account_type", "purchase_account"),
            ("discount_received_account_type", "discount_received_account"),
            ("discount_allowed_account_type", "discount_allowed_account"),
        ]

        id_required = ["global", "category", "existing"]

        for obj in type_account_tuples:
            if attrs.get(obj[0]):
                if attrs.get(obj[0]).lower() in id_required and not attrs.get(obj[1]):
                    raise ValidationError({obj[1]: ["This field cannot be empty."]})

        return attrs

    @staticmethod
    def base64_check(validated_data, attributes):
        for attr in attributes:
            if validated_data.get(attr) and not isinstance(
                validated_data.get(attr), ContentFile
            ):
                validated_data.pop(attr)
        return validated_data

    def update(self, instance, validated_data):
        validated_data = self.base64_check(
            validated_data, ["front_image", "back_image"]
        )
        return super().update(instance, validated_data)

    class Meta:
        model = Item
        exclude = (
            "company",
            "tax_scheme",
            "unit",
        )


class ItemSalesSerializer(BaseModelSerializer):
    rate = serializers.ReadOnlyField(source="selling_price")
    is_trackable = serializers.ReadOnlyField()
    default_unit_obj = GenericSerializer(read_only=True, source="unit")

    class Meta:
        model = Item
        fields = (
            "id",
            "name",
            "unit_id",
            "rate",
            "tax_scheme_id",
            "code",
            "description",
            "is_trackable",
            "default_unit_obj",
        )


class ItemOpeningSerializer(BaseModelSerializer):
    name = serializers.ReadOnlyField(source="item.name")
    item_id = serializers.ReadOnlyField(source="item.id")

    class Meta:
        model = InventoryAccount
        fields = ("id", "name", "item_id", "opening_balance", "opening_balance_rate")

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ItemPOSSerializer(BaseModelSerializer):
    rate = serializers.ReadOnlyField(source="selling_price")

    class Meta:
        model = Item
        fields = ("id", "name", "unit_id", "rate", "tax_scheme_id", "code")


class ItemPurchaseSerializer(BaseModelSerializer):
    rate = serializers.ReadOnlyField(source="cost_price")
    is_trackable = serializers.ReadOnlyField()
    default_unit_obj = GenericSerializer(read_only=True, source="unit")

    class Meta:
        model = Item
        fields = (
            "id",
            "name",
            "unit_id",
            "rate",
            "code",
            "tax_scheme_id",
            "description",
            "is_trackable",
            "track_inventory",
            "default_unit_obj",
        )


class BookSerializer(ItemSerializer):
    def create(self, validated_data):
        request = self.context["request"]
        category = Category.objects.filter(
            name="Book", company=request.user.company
        ).first()
        if not category:
            category = create_book_category(request.company)
        validated_data["category"] = category

        acc_system_codes = settings.ACCOUNT_SYSTEM_CODES
        if category.items_purchase_account_type == "global":
            validated_data["purchase_account"] = Account.objects.get(
                system_code=acc_system_codes["Purchase Account"]
            )

        if category.items_sales_account_type == "global":
            validated_data["sales_account"] = Account.objects.get(
                system_code=acc_system_codes["Sales Account"]
            )

        if category.items_discount_allowed_account_type == "global":
            validated_data["discount_allowed_account"] = Account.objects.get(
                system_code=acc_system_codes["Discount Expenses"],
            )

        if category.items_discount_received_account_type == "global":
            validated_data["discount_received_account"] = Account.objects.get(
                system_code=acc_system_codes["Discount Income"],
            )

        instance = super(BookSerializer, self).create(validated_data)
        return instance


class UnitSerializer(BaseModelSerializer):
    class Meta:
        model = Unit
        exclude = ("company",)


class InventoryCategorySerializer(BaseModelSerializer):
    default_unit_id = serializers.IntegerField(required=False, allow_null=True)
    default_tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    selected_default_unit_obj = UnitSerializer(read_only=True, source="default_unit")
    selected_default_tax_scheme_obj = GenericSerializer(
        read_only=True, source="default_tax_scheme"
    )

    def validate(self, attrs):
        type_account_tuples = [
            ("items_sales_account_type", "sales_account"),
            ("items_purchase_account_type", "purchase_account"),
            ("item_discount_received_account_type", "discount_received_account"),
            ("item_sdiscount_allowed_account_type", "discount_allowed_account"),
        ]

        id_required = ["global", "existing"]

        for obj in type_account_tuples:
            if attrs.get(obj[0]):
                if attrs.get(obj[0]).lower() in id_required and not attrs.get(obj[1]):
                    raise ValidationError({obj[1]: ["This field cannot be empty."]})

        return attrs

    class Meta:
        model = InventoryCategory
        exclude = (
            "company",
            "default_unit",
            "default_tax_scheme",
            "sales_account_category",
            "purchase_account_category",
            "discount_allowed_account_category",
            "discount_received_account_category",
            "fixed_asset_account_category",
            "direct_expense_account_category",
            "indirect_expense_account_category",
        )


class InventoryCategoryFormSerializer(InventoryCategorySerializer):
    selected_default_unit_obj = UnitSerializer(read_only=True, source="default_unit")
    selected_default_tax_scheme_obj = GenericSerializer(
        read_only=True, source="default_tax_scheme"
    )
    sales_account_obj = AccountMinSerializer(read_only=True, source="sales_account")
    purchase_account_obj = AccountMinSerializer(
        read_only=True, source="purchase_account"
    )
    discount_allowed_account_obj = AccountMinSerializer(
        read_only=True, source="discount_allowed_account"
    )
    discount_received_account_obj = AccountMinSerializer(
        read_only=True, source="discount_received_account"
    )


class ItemFormSerializer(ItemSerializer):
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")
    selected_sales_account_obj = AccountMinSerializer(
        read_only=True, source="sales_account"
    )
    selected_purchase_account_obj = AccountMinSerializer(
        read_only=True, source="purchase_account"
    )
    selected_discount_received_account_obj = AccountMinSerializer(
        read_only=True, source="discount_received_account"
    )
    selected_discount_allowed_account_obj = AccountMinSerializer(
        read_only=True, source="discount_allowed_account"
    )
    selected_inventory_category_obj = InventoryCategoryFormSerializer(
        read_only=True, source="category"
    )
    selected_brand_obj = GenericSerializer(read_only=True, source="brand")


class InventoryCategoryTrialBalanceSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = ("name", "id", "can_be_sold", "can_be_purchased", "fixed_asset")


class BrandSerializer(BaseModelSerializer):
    class Meta:
        model = Brand
        exclude = ("company",)


class InventoryAccountSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryAccount
        fields = (
            "account_no",
            "code",
            "current_balance",
            "id",
            "name",
            "opening_balance",
            "item",
        )


class InventoryAccountBalanceSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryAccount
        fields = ("id", "amounts")


class ItemDetailSerializer(BaseModelSerializer):
    brand = BrandSerializer()
    category = InventoryCategorySerializer()
    unit = UnitSerializer()
    account = InventoryAccountBalanceSerializer()

    discount_allowed_account = AccountBalanceSerializer()
    discount_received_account = AccountBalanceSerializer()

    sales_account = AccountBalanceSerializer()
    purchase_account = AccountBalanceSerializer()
    expense_account = AccountBalanceSerializer()
    fixed_asset_account = AccountBalanceSerializer()
    tax_scheme = TaxSchemeSerializer()

    class Meta:
        model = Item
        exclude = ("company",)


class ItemListSerializer(BaseModelSerializer):
    category = GenericSerializer()

    class Meta:
        model = Item
        fields = ("id", "name", "category", "cost_price", "selling_price", "code")


class ItemListMinSerializer(BaseModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f"{obj.name} ({obj.code})"

    class Meta:
        model = Item
        fields = ["id", "name", "code"]


class JournalEntrySerializer(BaseModelSerializer):
    dr_amount = serializers.SerializerMethodField()
    cr_amount = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    voucher_type = serializers.SerializerMethodField()
    voucher_no = serializers.ReadOnlyField(source="source.get_voucher_no")
    source_id = serializers.ReadOnlyField(source="source.get_source_id")

    def get_voucher_type(self, obj):
        v_type = obj.content_type.name
        if v_type[-4:] == " row":
            v_type = v_type[:-3]
        if v_type[-11:] == " particular":
            v_type = v_type[:-10]
        if v_type == "account":
            return "Opening Balance"
        return v_type.title()

    def transaction(self, obj):
        account = self.context.get("account", None)
        try:
            transactions = [
                transaction
                for transaction in obj.transactions.all()
                if transaction.account.id == account.id
            ]
            if transactions:
                return transactions[0]
        except Exception:
            return

    def get_dr_amount(self, obj):
        amount = "-"
        transaction = self.transaction(obj)
        if transaction:
            amount = transaction.dr_amount
        return amount

    def get_cr_amount(self, obj):
        amount = "-"
        transaction = self.transaction(obj)
        if transaction:
            amount = transaction.cr_amount
        return amount

    def get_balance(self, obj):
        amount = "-"
        transaction = self.transaction(obj)
        if transaction:
            amount = transaction.get_balance()
        return amount

    class Meta:
        model = JournalEntry
        fields = "__all__"


class TransactionEntrySerializer(BaseModelSerializer):
    date = serializers.ReadOnlyField(source="journal_entry.date")
    source_type = serializers.SerializerMethodField()
    source_id = serializers.ReadOnlyField(source="journal_entry.source.get_source_id")

    # voucher_no is too expensive on DB -
    voucher_no = serializers.ReadOnlyField(source="journal_entry.source.get_voucher_no")

    def get_source_type(self, obj):
        v_type = obj.journal_entry.content_type.name
        if v_type[-4:] == " row":
            v_type = v_type[:-3]
        if v_type[-11:] == " particular":
            v_type = v_type[:-10]
        if v_type == "account":
            return "Opening Balance"
        return v_type.strip().title()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "dr_amount",
            "cr_amount",
            "current_balance",
            "date",
            "source_type",
            "account_id",
            "source_id",
            "voucher_no",
        )


class InventorySettingCreateSerializer(BaseModelSerializer):
    class Meta:
        model = InventorySetting
        exclude = ["company"]


class BillOfMaterialRowSerializer(BaseModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = BillOfMaterialRow
        exclude = ("item", "unit", "bill_of_material")


class BillOfMaterialCreateSerializer(BaseModelSerializer):
    unit_id = serializers.IntegerField(required=True)
    rows = BillOfMaterialRowSerializer(many=True)
    finished_product_name = serializers.ReadOnlyField(source="finished_product.name")

    def validate(self, data):
        finished_product = data.get("finished_product")
        for row in data["rows"]:
            if row["item_id"] == finished_product.id:
                raise ValidationError(
                    {
                        "detail": "Finished product cannot be part of its own bill of material."
                    }
                )
        return data

    def create(self, validated_data):
        rows = validated_data.pop("rows")
        instance = BillOfMaterial.objects.create(**validated_data)
        for row in rows:
            BillOfMaterialRow.objects.create(bill_of_material=instance, **row)
        return instance

    def update(self, instance, validated_data):
        rows = validated_data.pop("rows")
        validated_data.pop("finished_product")
        for row in rows:
            BillOfMaterialRow.objects.update_or_create(
                bill_of_material=instance, pk=row.get("id"), defaults=row
            )
        return super().update(instance, validated_data)

    class Meta:
        model = BillOfMaterial
        exclude = ("company", "unit")


class BillOfMaterialListSerializer(BaseModelSerializer):
    item = serializers.ReadOnlyField(source="finished_product.name")

    class Meta:
        model = BillOfMaterial
        fields = ["id", "item"]


class InventoryAdjustmentVoucherRowSerializer(BaseModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=True)
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")
    selected_item_obj = GenericSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")

    class Meta:
        model = InventoryAdjustmentVoucherRow
        exclude = (
            "item",
            "voucher",
            "unit",
        )


class InventoryAdjustmentVoucherCreateSerializer(BaseModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = InventoryAdjustmentVoucherRowSerializer(many=True)
    total_amount = serializers.ReadOnlyField()

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            InventoryAdjustmentVoucher, self.context["request"].company.id
        )
        validated_data["voucher_no"] = next_voucher_no

    def validate(self, data):
        request = self.context["request"]
        data = super().validate(data)
        inventory_setting = request.company.inventory_setting
        item_ids = {row["item_id"] for row in data["rows"]}
        if (
            inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
            and not data.get("purpose") == "Stock In"
        ):
            quantities = {}
            for row in data["rows"]:
                item_id = row["item_id"]
                quantity = row["quantity"]
                if quantities.get(item_id):
                    quantities[item_id] += quantity
                else:
                    quantities[item_id] = quantity
            items = (
                Item.objects.filter(id__in=item_ids)
                .annotate(remaining=F("account__current_balance"))
                .only("id")
            )
            remaining_stock_map = {item.id: item.remaining for item in items}
            for item in items:
                if remaining_stock_map[item.id] < quantities[item.id]:
                    raise UnprocessableException(
                        detail=f"You do not have enough stock for item {item.name} in your inventory to create this sales. Available stock: {item.remaining} {item.unit.name if item.unit else 'units'}",
                        code="negative_stock",
                    )

        if inventory_setting.enable_fifo and not request.query_params.get(
            "fifo_inconsistency"
        ):
            date = datetime.datetime.strptime(request.data["date"], "%Y-%m-%d")
            items_transactions = Transaction.objects.filter(
                Q(account__item__id__in=item_ids) & Q(journal_entry__date__gt=date)
            )
            if items_transactions.exists():
                raise UnprocessableException(
                    detail="There are Transactions on later dates. This might create insonsistencies in FIFO.",
                    code="fifo_inconsistency",
                )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_voucher_number(validated_data, instance=None)
        instance = InventoryAdjustmentVoucher.objects.create(**validated_data)
        total_amount = 0
        for index, row in enumerate(rows_data):
            if row.get("id"):
                row.pop("id")
            quantity = row.get("quantity")
            rate = row.get("rate")
            total_amount += rate * quantity
            InventoryAdjustmentVoucherRow.objects.create(voucher=instance, **row)
        instance.total_amount = total_amount
        instance.save()
        instance.apply_transactions()
        return instance

    def update(self, instance, validated_data):
        # prevent form updating purpose
        validated_data.pop("purpose")
        rows_data = validated_data.pop("rows")
        total_amount = 0
        InventoryAdjustmentVoucher.objects.filter(pk=instance.id).update(
            **validated_data
        )
        for index, row in enumerate(rows_data):
            InventoryAdjustmentVoucherRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
            quantity = row.get("quantity")
            rate = row.get("rate")
            total_amount += rate * quantity
        if instance.total_amount != total_amount:
            instance.total_amount = total_amount
            instance.save()
        instance.apply_transactions()
        return instance

    class Meta:
        model = InventoryAdjustmentVoucher
        exclude = ("company",)


class InventoryAdjustmentVoucherListSerializer(BaseModelSerializer):
    class Meta:
        model = InventoryAdjustmentVoucher
        fields = ["id", "voucher_no", "date", "status", "purpose", "total_amount"]


class InventoryAdjustmentVoucherDetailSerializer(BaseModelSerializer):
    rows = InventoryAdjustmentVoucherRowSerializer(many=True)

    class Meta:
        model = InventoryAdjustmentVoucher
        exclude = ("company",)


class InventoryConversionVoucherRowSerializer(BaseModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=True)
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")

    def validate(self, attrs):
        transaction_type = attrs.get("transaction_type")
        rate = attrs.get("rate", None)

        if transaction_type == "Dr" and not rate:
            raise serializers.ValidationError(
                {"rate": "Rate is required for debit transaction."}
            )

        if transaction_type == "Cr" and rate:
            raise serializers.ValidationError(
                {"detail": "Rate is not allowed for credit transaction."}
            )

        return super().validate(attrs)

    class Meta:
        model = InventoryConversionVoucherRow
        exclude = (
            "item",
            "voucher",
            "unit",
        )


class InventoryConversionVoucherCreateSerializer(BaseModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = InventoryConversionVoucherRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            InventoryConversionVoucher, self.context["request"].company.id
        )
        validated_data["voucher_no"] = next_voucher_no

    def validate(self, data):
        request = self.context["request"]
        bill_of_material = data.get("finished_product", None)
        if bill_of_material is not None:
            finished_product = bill_of_material.finished_product

        dr_item_ids = []
        cr_item_ids = []

        for row in data["rows"]:
            if row.get("transaction_type") == "Dr":
                dr_item_ids.append(row["item_id"])
            else:
                cr_item_ids.append(row["item_id"])

        if (not cr_item_ids) or (not dr_item_ids):
            raise ValidationError(
                {"detail": "Finished product and raw material are required"}
            )

        if finished_product is not None:
            for item_id in dr_item_ids:
                if item_id != finished_product.id:
                    dr_item_ids.append(finished_product.id)

        for row in data["rows"]:
            if row["item_id"] in cr_item_ids and row["item_id"] in dr_item_ids:
                raise ValidationError(
                    {
                        "detail": "Finished product and raw material cannot have same item"
                    }
                )

        quantities = {
            row["item_id"]: row["quantity"]
            for row in data["rows"]
            if row.get("transaction_type") == "Cr"
        }

        # Check negative stock
        inventory_setting = request.company.inventory_setting
        if (
            inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
        ):
            items = (
                Item.objects.filter(id__in=cr_item_ids)
                .annotate(remaining=F("account__current_balance"))
                .only("id")
            )

            remaining_stock_map = {item.id: item.remaining for item in items}

            for item in items:
                if remaining_stock_map[item.id] < quantities[item.id]:
                    raise UnprocessableException(
                        detail=f"You do not have enough stock for item {item.name} in your inventory to create this sales. Available stock: {item.remaining} {item.unit.name if item.unit else 'units'}",
                        code="negative_stock",
                    )

        if inventory_setting.enable_fifo and not request.query_params.get(
            "fifo_inconsistency"
        ):
            item_ids = [row["item_id"] for row in data["rows"]]
            date = datetime.datetime.strptime(request.data["date"], "%Y-%m-%d")
            items_transactions = Transaction.objects.filter(
                Q(account__item__id__in=item_ids) & Q(journal_entry__date__gt=date)
            )
            if items_transactions.exists():
                raise UnprocessableException(
                    detail="There are Transactions on later dates. This might create insonsistencies in FIFO.",
                    code="fifo_inconsistency",
                )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_voucher_number(validated_data, instance=None)
        instance = InventoryConversionVoucher.objects.create(**validated_data)
        for row in rows_data:
            if row.get("id"):
                row.pop("id")
            InventoryConversionVoucherRow.objects.create(voucher=instance, **row)
        instance.apply_inventory_transactions()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # prevent form updating finished_product
        validated_data.pop("finished_product", None)
        rows_data = validated_data.pop("rows")
        InventoryConversionVoucher.objects.filter(pk=instance.id).update(
            **validated_data
        )
        for row in rows_data:
            InventoryConversionVoucherRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
            instance.apply_inventory_transactions()
            instance.save()
        return instance

    class Meta:
        model = InventoryConversionVoucher
        exclude = ("company",)


class InventoryConversionVoucherListSerializer(BaseModelSerializer):
    finished_product_name = serializers.ReadOnlyField(
        source="finished_product.finished_product.name"
    )

    class Meta:
        model = InventoryConversionVoucher
        fields = [
            "id",
            "voucher_no",
            "date",
            "status",
            "finished_product_name",
        ]


class InventoryConversionVoucherDetailSerializer(BaseModelSerializer):
    rows = InventoryConversionVoucherRowSerializer(many=True)
    finished_product_name = serializers.ReadOnlyField(
        source="finished_product.finished_product.name"
    )

    class Meta:
        model = InventoryConversionVoucher
        exclude = ("company",)


class InventoryConversionFinishedProductList(serializers.Serializer):
    name = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        fields = ("id", "name")
