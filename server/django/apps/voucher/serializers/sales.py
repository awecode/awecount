import datetime

from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.bank.models import ChequeDeposit
from apps.product.models import Item
from apps.tax.serializers import TaxSchemeSerializer
from apps.voucher.models import Challan, ChallanRow, PaymentReceipt, SalesAgent
from awecount.libs import get_next_voucher_no
from awecount.libs.exception import UnprocessableException
from awecount.libs.serializers import StatusReversionMixin

from ..models import (
    PurchaseVoucher,
    SalesDiscount,
    SalesVoucher,
    SalesVoucherRow,
)
from ..models.invoice_design import InvoiceDesign
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin


class SalesDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDiscount
        exclude = ("company",)
        extra_kwargs = {"name": {"required": True}}


class SalesDiscountMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDiscount
        fields = ("id", "name", "type", "value")


class PaymentReceiptSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    invoices = serializers.SerializerMethodField()

    def get_invoices(self, obj):
        invoices = []
        for invoice in obj.invoices.all():
            invoices.append({"id": invoice.id, "voucher_no": invoice.voucher_no})
        return invoices

    class Meta:
        model = PaymentReceipt
        fields = (
            "id",
            "date",
            "status",
            "mode",
            "party_name",
            "amount",
            "tds_amount",
            "invoices",
        )


class PaymentReceiptDetailSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    party_address = serializers.ReadOnlyField(source="party.address")
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    invoices = serializers.SerializerMethodField()
    cheque_date = serializers.ReadOnlyField(source="cheque_deposit.cheque_date")
    cheque_number = serializers.ReadOnlyField(source="cheque_deposit.cheque_number")
    drawee_bank = serializers.ReadOnlyField(source="cheque_deposit.drawee_bank")

    def get_invoices(self, obj):
        data = []
        for invoice in obj.invoices.all():
            data.append(
                {
                    "voucher_no": invoice.voucher_no,
                    "total_amount": invoice.total_amount,
                    "date": invoice.date,
                    "id": invoice.id,
                }
            )
        return data

    class Meta:
        model = PaymentReceipt
        fields = (
            "id",
            "date",
            "status",
            "mode",
            "party_name",
            "invoices",
            "amount",
            "tds_amount",
            "bank_account_name",
            "cheque_date",
            "party_address",
            "cheque_number",
            "drawee_bank",
            "cheque_deposit_id",
        )


class PaymentReceiptFormSerializer(serializers.ModelSerializer):
    cheque_date = serializers.DateField(required=False, source="cheque_deposit.date")
    cheque_number = serializers.CharField(
        required=False, source="cheque_deposit.cheque_number"
    )
    drawee_bank = serializers.CharField(
        required=False, source="cheque_deposit.drawee_bank"
    )
    remarks = serializers.CharField(required=False)
    party_name = serializers.ReadOnlyField(source="party.name")
    invoice_nos = serializers.SerializerMethodField()

    def get_invoice_nos(self, obj):
        return [invoice.voucher_no for invoice in obj.invoices.all()]

    def validate(self, data):
        party_id = None
        self.invoice_ids = []
        self.total_amount = 0
        for invoice in data.get("invoices"):
            if not (self.instance and self.instance.id) and invoice.status == "Paid":
                raise ValidationError({"invoice": "Invoice has already been paid"})
            if invoice.status == "Cancelled":
                raise ValidationError({"invoice": "Invoice has already been cancelled"})
            if party_id and invoice.party_id != party_id:
                raise ValidationError(
                    {
                        "invoice": "A single payment receipt can be issued to a single party only!"
                    }
                )
            party_id = invoice.party_id
            self.invoice_ids.append(invoice.id)
            self.total_amount += invoice.total_amount

        if data.get("mode") == "Cheque":
            if not data.get("cheque_deposit").get("date"):
                raise ValidationError({"cheque_date": "Cheque date is required."})
            if not data.get("cheque_deposit").get("cheque_number"):
                raise ValidationError({"cheque_number": "Cheque number is required."})
            if not data.get("cheque_deposit").get("drawee_bank"):
                raise ValidationError({"drawee_bank": "Drawee bank is required."})

        if data.get("mode") in ["Cheque", "Bank Deposit"]:
            if not data.get("bank_account"):
                raise ValidationError({"bank_account": "Bank account is required."})
        else:
            for field in ["cheque_date", "cheque_number", "drawee_bank"]:
                data.pop(field, None)
        data["party_id"] = party_id

        return data

    def save(self, **kwargs):
        cheque_deposit_data = self.validated_data.pop("cheque_deposit", {})
        if self.validated_data["mode"] == "Cheque":
            cheque_deposit_data["bank_account"] = self.validated_data["bank_account"]
        instance = super().save(**kwargs)
        if instance.amount >= self.total_amount and instance.mode in [
            "Cash",
            "Bank Deposit",
        ]:
            instance.invoices.update(status="Paid")
            instance.status = "Cleared"
            instance.save()
        # elif instance.amount and len(self.invoice_ids) === 1:
        #     instance.invoices.update(status='Partially Paid')
        if self.validated_data["mode"] == "Cheque":
            cheque_deposit = instance.cheque_deposit or ChequeDeposit(
                company_id=self.context["request"].company_id, status="Issued"
            )
            cheque_deposit.date = instance.date
            cheque_deposit.bank_account = instance.bank_account
            cheque_deposit.cheque_date = cheque_deposit_data.get("date")
            cheque_deposit.cheque_number = cheque_deposit_data.get("cheque_number")
            cheque_deposit.drawee_bank = cheque_deposit_data.get("drawee_bank")
            cheque_deposit.amount = instance.amount
            cheque_deposit.benefactor = instance.party.customer_account
            cheque_deposit.save()
            cheque_deposit.apply_transactions()
            if not instance.cheque_deposit:
                instance.cheque_deposit = cheque_deposit
                instance.save()
        instance.apply_transactions()
        return instance

    class Meta:
        model = PaymentReceipt
        fields = (
            "id",
            "date",
            "invoices",
            "amount",
            "tds_amount",
            "bank_account",
            "cheque_date",
            "cheque_number",
            "drawee_bank",
            "remarks",
            "mode",
            "party_id",
            "party_name",
            "invoice_nos",
        )


class SalesVoucherRowSerializer(
    DiscountObjectTypeSerializerMixin, serializers.ModelSerializer
):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)
    item_name = serializers.ReadOnlyField(source="item.name")
    amount_before_tax = serializers.ReadOnlyField()
    amount_before_discount = serializers.ReadOnlyField()

    def validate_discount(self, value):
        if not value:
            value = 0
        elif value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value

    class Meta:
        model = SalesVoucherRow
        exclude = ("item", "tax_scheme", "voucher", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class SalesVoucherRowAccessSerializer(SalesVoucherRowSerializer):
    item_id = serializers.IntegerField(required=False)
    item_obj = serializers.DictField(required=False)
    item_code = serializers.ReadOnlyField(source="item.code")

    def validate(self, data):
        data = super().validate(data)
        if "item_id" not in data:
            if "item_obj" not in data:
                raise ValidationError({"item": ["item_id or item_obj is required."]})
            if "code" not in data["item_obj"]:
                raise ValidationError({"item": ["item_obj.code is required."]})
            try:
                item_obj = Item.objects.get(
                    code=data["item_obj"].get("code"),
                    company_id=self.context["request"].company_id,
                )
                # if data['item_obj'].get('name') and item_obj.name != data['item_obj'].get('name'):
                #     item_obj.name = data['item_obj'].get('name')
                #     item_obj.save()
            except Item.DoesNotExist:
                item_obj = Item.objects.create(
                    code=str(data["item_obj"].get("code")),
                    name=str(
                        data["item_obj"].get("name") or data["item_obj"].get("code")
                    ),
                    unit_id=data["unit_id"],
                    category_id=data.get("category_id"),
                    selling_price=data["rate"],
                    tax_scheme_id=data["tax_scheme_id"],
                    company_id=self.context["request"].company_id,
                )
            data["item_id"] = item_obj.id
            del data["item_obj"]

        return data


class SalesVoucherCreateSerializer(
    StatusReversionMixin,
    DiscountObjectTypeSerializerMixin,
    ModeCumBankSerializerMixin,
    serializers.ModelSerializer,
):
    voucher_no = serializers.ReadOnlyField()
    print_count = serializers.ReadOnlyField()
    rows = SalesVoucherRowSerializer(many=True)
    voucher_meta = serializers.ReadOnlyField()
    challan_numbers = serializers.ReadOnlyField(source="challan_voucher_numbers")

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get("status") in ["Draft", "Cancelled"]:
            return
        next_voucher_no = get_next_voucher_no(
            SalesVoucher, self.context["request"].company_id
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
        # TODO: Find why due date is null and fix the issue
        request = self.context["request"]
        # request_data = self.context["request"].data
        if "due_date" not in request.data.keys():
            data["due_date"] = None
        else:
            data["due_date"] = request.data["due_date"]
        if (
            not data.get("party")
            and data.get("mode") == "Credit"
            and data.get("status") != "Draft"
        ):
            raise ValidationError(
                {"party": ["Party is required for a credit issue."]},
            )

        if data.get("discount") and data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})

        item_ids = [row["item_id"] for row in data["rows"]]
        quantities = {row["item_id"]: row["quantity"] for row in data["rows"]}

        inventory_setting = request.company.inventory_setting

        if inventory_setting.enable_fifo and not request.query_params.get(
            "fifo_inconsistency"
        ):
            date = datetime.datetime.strptime(request.data["date"], "%Y-%m-%d")

            sales_rows_exists = (
                SalesVoucherRow.objects.filter(
                    item_id__in=item_ids, voucher__date__gt=date
                )
                .exclude(voucher__status__in=["Draft", "Cancelled"])
                .exists()
            )

            challan_rows_exists = ChallanRow.objects.filter(
                item_id__in=item_ids, voucher__date__gt=date, voucher__status="Issued"
            ).exists()

            if sales_rows_exists or challan_rows_exists:
                raise UnprocessableException(
                    detail="There are Challans or SalesVouchers on later dates. This might create insonsistencies in FIFO.",
                    code="fifo_inconsistency",
                )

        # Check negative stock
        if (
            inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
        ):
            items = (
                Item.objects.filter(id__in=item_ids)
                .annotate(remaining_stock=F("account__current_balance"))
                .only("remaining_stock", "id")
            )

            remaining_stock_map = {item.id: item.remaining_stock for item in items}

            for item in items:
                if remaining_stock_map[item.id] < quantities[item.id]:
                    raise UnprocessableException(
                        detail=f"You do not have enough stock for item {item.name} in your inventory to create this sales. Available stock: {item.remaining_stock} {item.unit.name if item.unit else 'units'}",
                        code="negative_stock",
                    )

        return data

    def validate_invoice_date(self, data, voucher_no=None):
        # Check if there are invoices in later date
        if data.get("status") == "Issued":
            qs = SalesVoucher.objects.filter(
                date__gt=data.get("date"),
                fiscal_year_id=data.get("fiscal_year_id"),
                company_id=data.get("company_id"),
            )
            if voucher_no:
                qs = qs.filter(voucher_no__lt=voucher_no)
                # if qs.exists():
                #     raise ValidationError(
                #         {'date': ['Invoice with later date already exists!']},
                #     )

    def validate_rows(self, rows):
        for row in rows:
            row_serializer = SalesVoucherRowSerializer(data=row)
            if not row_serializer.is_valid():
                raise serializers.ValidationError(row_serializer.errors)
        return rows

    def validate_due_date(self, due_date):
        if due_date:
            if isinstance(due_date, str):
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
            validation_date = (
                self.instance.due_date if self.instance else timezone.now().date()
            )
            if due_date < validation_date:
                raise ValidationError("Due date cannot be before invoice date.")

    def check_challans(self, challans, rows):
        voucher_items = []
        challan_items = []
        for row in rows:
            voucher_items.append((row.get("item_id"), row.get("quantity")))

        voucher_items_ids = [x[0] for x in voucher_items]
        for challan in challans:
            rows = challan.rows.values_list("item_id", "quantity")
            items_list = [x for x in rows]
            for row in items_list:
                challan_items.append(row)
                if row[0] not in voucher_items_ids:
                    raise serializers.ValidationError(
                        {"detail": "Items cannot be deleted while importing challan."}
                    )
                desired_tuple = next(
                    (tup for tup in voucher_items if tup[0] == row[0]), None
                )
                if not desired_tuple:
                    raise serializers.ValidationError(
                        {"detail": "Items cannot be added while importing challan."}
                    )
                if desired_tuple[1] != row[1]:
                    raise serializers.ValidationError(
                        {
                            "detail": "The quantity cannot be changed while importing challan."
                        }
                    )

        if len(challan_items) < len(voucher_items):
            raise serializers.ValidationError(
                {"detail": "Items cannot be added while importing challan."}
            )
        return

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
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
        instance.apply_transactions(voucher_meta=meta)
        # TODO: synchronize with CBMS
        # instance.synchronize()
        return instance

    def update(self, instance, validated_data):
        if validated_data["status"] == "Issued":
            if not instance.company.current_fiscal_year == instance.fiscal_year:
                instance.fiscal_year = instance.company.current_fiscal_year
                instance.issue_datetime = timezone.now
                instance.date = timezone.now().date
        rows_data = validated_data.pop("rows")
        challans = validated_data.pop("challans", None)
        self.assign_fiscal_year(validated_data, instance=instance)
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        # Check if there are invoices in later date
        validated_data["company_id"] = self.context["request"].company_id
        validated_data["fiscal_year_id"] = instance.fiscal_year_id
        self.validate_invoice_date(validated_data, voucher_no=instance.voucher_no)
        # self.validate_due_date(validated_data['due_date'], instance=instance)
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)

        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            SalesVoucherRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
            # if not request.data.get("invoices"):

        if challans:
            instance.challans.clear()
            instance.challans.add(*challans)

        instance.refresh_from_db()
        meta = instance.generate_meta(update_row_data=True)
        instance.apply_transactions(voucher_meta=meta)
        # instance.synchronize(verb='PATCH')
        return instance

    class Meta:
        model = SalesVoucher
        exclude = (
            "company",
            "user",
            "bank_account",
            "discount_obj",
            "fiscal_year",
        )


class SalesVoucherAccessSerializer(SalesVoucherCreateSerializer):
    """
    {"mode":"Cash","customer_name":"","status":"Issued","address":"ASD","discount_type":null,"discount":0,"is_export":false,"date":"2019-11-07","due_date":"2019-11-07","rows":[{"quantity":1,"discount":0,"discount_type":null,"trade_discount":false,"item_id":401,"tax_scheme_id":45,"rate":500,"unit_id":25,"description":""}],"trade_discount":true}

    """

    date = serializers.DateField(default=datetime.datetime.today().date)
    rows = SalesVoucherRowAccessSerializer(many=True)
    pdf_url = serializers.ReadOnlyField()
    view_url = serializers.ReadOnlyField()


class SalesAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAgent
        exclude = ("company",)


class SalesVoucherRowDetailSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField()
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")
    discount_obj = SalesDiscountSerializer()
    tax_scheme = TaxSchemeSerializer()

    class Meta:
        model = SalesVoucherRow
        exclude = ("voucher", "item", "unit")


class SalesVoucherDetailSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    discount_obj = SalesDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")
    sales_agent = SalesAgentSerializer()

    rows = SalesVoucherRowDetailSerializer(many=True)
    tax_registration_number = serializers.ReadOnlyField(
        source="party.tax_registration_number"
    )
    enable_row_description = serializers.ReadOnlyField(
        source="company.sales_setting.enable_row_description"
    )

    payment_receipts = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    fiscal_year = serializers.StringRelatedField()
    invoice_footer_text = serializers.ReadOnlyField(
        source="company.sales_setting.invoice_footer_text"
    )
    challan_numbers = serializers.ReadOnlyField(source="challan_voucher_numbers")

    def get_payment_receipts(self, obj):
        receipts = []
        if hasattr(obj, "receipts"):
            for receipt in obj.receipts:
                receipts.append(
                    {
                        "id": receipt.id,
                        "amount": receipt.amount,
                        "tds_amount": receipt.tds_amount,
                        "status": receipt.status,
                    }
                )
        return receipts

    def get_options(self, obj):
        options = {}
        amt_qt_setting = obj.company.sales_setting.show_rate_quantity_in_voucher
        options["show_rate_quantity_in_voucher"] = amt_qt_setting
        return options

    class Meta:
        model = SalesVoucher
        exclude = (
            "company",
            "user",
            "bank_account",
        )


class SalesVoucherChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesVoucher
        fields = ("id", "voucher_no", "date", "status", "customer_name", "total_amount")


class SalesVoucherListSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    payment_receipts = serializers.SerializerMethodField()

    def get_payment_receipts(self, obj):
        receipts = []
        for receipt in obj.receipts:
            receipts.append(
                {
                    "id": receipt.id,
                    "amount": receipt.amount,
                    "tds_amount": receipt.tds_amount,
                    "status": receipt.status,
                }
            )
        return receipts

    class Meta:
        model = SalesVoucher
        fields = (
            "id",
            "voucher_no",
            "party_name",
            "date",
            "status",
            "customer_name",
            "total_amount",
            "payment_receipts",
        )


class SaleVoucherOptionsSerializer(serializers.ModelSerializer):
    value = serializers.ReadOnlyField(source="pk")
    text = serializers.ReadOnlyField(source="voucher_no")

    class Meta:
        model = SalesVoucher
        fields = (
            "value",
            "text",
        )


class InvoiceDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDesign
        exclude = ("company",)


class SalesBookSerializer(serializers.ModelSerializer):
    buyers_name = serializers.ReadOnlyField(source="buyer_name")
    buyers_pan = serializers.ReadOnlyField(source="party.tax_registration_number")
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")

    class Meta:
        model = SalesVoucher
        fields = (
            "id",
            "date",
            "buyers_name",
            "buyers_pan",
            "voucher_no",
            "voucher_meta",
            "is_export",
            "meta_discount",
            "meta_tax",
            "meta_taxable",
        )


class SalesBookExportSerializer(serializers.ModelSerializer):
    buyers_name = serializers.ReadOnlyField(source="buyer_name")
    buyers_pan = serializers.ReadOnlyField(source="party.tax_registration_number")
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")
    item_names = serializers.ReadOnlyField()
    total_quantity = serializers.SerializerMethodField()

    def get_total_quantity(self, obj):
        # Annotate this on queryset on api that uses this serializer
        return obj.total_quantity

    class Meta:
        model = SalesVoucher
        fields = (
            "date",
            "buyers_name",
            "buyers_pan",
            "voucher_no",
            "voucher_meta",
            "is_export",
            "item_names",
            "units",
            "total_quantity",
            "status",
        )


class PurchaseBookSerializer(serializers.ModelSerializer):
    sellers_name = serializers.ReadOnlyField(source="party.name")
    sellers_pan = serializers.ReadOnlyField(source="party.tax_registration_number")
    voucher_meta = serializers.ReadOnlyField(source="get_voucher_meta")

    class Meta:
        model = PurchaseVoucher
        fields = (
            "id",
            "date",
            "sellers_name",
            "sellers_pan",
            "voucher_no",
            "voucher_meta",
            "is_import",
        )


class SalesRowSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.name")
    buyers_name = serializers.ReadOnlyField(source="voucher.buyer_name")
    buyers_pan = serializers.ReadOnlyField(
        source="voucher.party.tax_registration_number"
    )
    voucher__voucher_no = serializers.CharField(source="voucher.voucher_no")
    voucher__date = serializers.CharField(source="voucher.date")

    class Meta:
        model = SalesVoucherRow
        fields = (
            "item",
            "buyers_name",
            "buyers_pan",
            "voucher__voucher_no",
            "voucher_id",
            "rate",
            "quantity",
            "voucher__date",
            "tax_amount",
            "discount_amount",
            "net_amount",
        )


class ChallanRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False)

    class Meta:
        model = ChallanRow
        exclude = (
            "item",
            "voucher",
            "unit",
        )


class ChallanListSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")

    class Meta:
        model = Challan
        fields = ("id", "voucher_no", "party_name", "date", "customer_name", "status")


class ChallanCreateSerializer(StatusReversionMixin, serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    print_count = serializers.ReadOnlyField()
    rows = ChallanRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        next_voucher_no = get_next_voucher_no(
            Challan, self.context["request"].company_id
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
            and data.get("mode") == "Credit"
            and data.get("status") != "Draft"
        ):
            raise ValidationError(
                {"party": ["Party is required for a credit issue."]},
            )
        if not (data.get("customer_name") or data.get("party")):
            raise ValidationError(
                {
                    "party": ["Party is required."],
                    "customer_name": ["Customer name is required."],
                }
            )

        request = self.context["request"]
        item_ids = [row["item_id"] for row in data["rows"]]
        quantities = {row["item_id"]: row["quantity"] for row in data["rows"]}

        inventory_setting = request.company.inventory_setting

        if inventory_setting.enable_fifo and not request.query_params.get(
            "fifo_inconsistency"
        ):
            date = datetime.datetime.strptime(request.data["date"], "%Y-%m-%d")

            sales_rows_exists = (
                SalesVoucherRow.objects.filter(
                    item_id__in=item_ids, voucher__date__gt=date
                )
                .exclude(voucher__status__in=["Draft", "Cancelled"])
                .exists()
            )

            challan_rows_exists = ChallanRow.objects.filter(
                item_id__in=item_ids, voucher__date__gt=date, voucher__status="Issued"
            ).exists()

            if sales_rows_exists or challan_rows_exists:
                raise UnprocessableException(
                    detail="There are Challans or SalesVouchers on later dates. This might create insonsistencies in FIFO.",
                    code="fifo_inconsistency",
                )

        if (
            inventory_setting.enable_negative_stock_check
            and not request.query_params.get("negative_stock")
        ):
            items = (
                Item.objects.filter(id__in=item_ids)
                .annotate(remaining_stock=F("account__current_balance"))
                .only("remaining_stock", "id")
            )

            remaining_stock_map = {item.id: item.remaining_stock for item in items}

            for item in items:
                if remaining_stock_map[item.id] < quantities[item.id]:
                    raise UnprocessableException(
                        detail=f"You do not have enough stock for item {item.name} in your inventory to create this sales. Available stock: {item.remaining_stock} {item.unit.name if item.unit else 'units'}",
                        code="negative_stock",
                    )

        return data

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        request = self.context["request"]
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        validated_data["company_id"] = request.company_id
        validated_data["user_id"] = request.user.id
        instance = Challan.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            ChallanRow.objects.create(voucher=instance, **row)
        instance.apply_inventory_transactions()
        # TODO: Sync with CBMS
        # instance.synchronize()
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows")
        self.assign_fiscal_year(validated_data, instance=instance)
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        Challan.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            ChallanRow.objects.update_or_create(
                voucher=instance, pk=row.get("id"), defaults=row
            )
        instance.refresh_from_db()
        instance.apply_inventory_transactions()
        # instance.synchronize(verb='PATCH')
        return instance

    class Meta:
        model = Challan
        exclude = (
            "company",
            "user",
            "fiscal_year",
        )
