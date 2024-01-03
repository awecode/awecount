from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from awecount.libs import get_next_voucher_no
from awecount.libs.serializers import StatusReversionMixin
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin
from .sales import SalesDiscountSerializer, SalesVoucherRowDetailSerializer
from ..models import CreditNoteRow, CreditNote, PurchaseVoucherRow


class CreditNoteRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
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
        exclude = ('item', 'tax_scheme', 'voucher', 'unit', 'discount_obj')
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False}
        }


class CreditNoteCreateSerializer(StatusReversionMixin, DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin,
                                 serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = CreditNoteRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance=None):
        if instance and instance.voucher_no:
            return
        if validated_data.get('status') in ['Draft', 'Cancelled']:
            return
        next_voucher_no = get_next_voucher_no(CreditNote, self.context['request'].company_id)
        validated_data['voucher_no'] = next_voucher_no

    def assign_fiscal_year(self, validated_data, instance=None):
        if instance and instance.fiscal_year_id:
            return
        fiscal_year = self.context['request'].company.current_fiscal_year
        if fiscal_year.includes(validated_data.get('date')):
            validated_data['fiscal_year_id'] = fiscal_year.id
        else:
            raise ValidationError(
                {'date': ['Date not in current fiscal year.']},
            )

    def validate(self, data):
        if not data.get('party') and data.get('mode') == 'Credit' and data.get('status') != 'Draft':
            raise ValidationError(
                {'party': ['Party is required for a credit issue.']},
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
    
    def cancel_sales(self, instance, rows_data):
        sales_vouchers = instance.invoices.all()
        for voucher in sales_vouchers:
            sales_rows = voucher.rows.all()
            for row in sales_rows:
                # sales_row_id = rows_data[row.id]
                row_data = next((item for item in rows_data if item['id'] == row.id), None)
                sold_items = row.sold_items
                quantity = row_data["quantity"]
                ob = None
                if sold_items.get("OB"):
                    ob = sold_items.pop("OB")
                purchase_row_ids = [key for key, value in sold_items.items()]
                purchase_voucher_rows = PurchaseVoucherRow.objects.filter(id__in=purchase_row_ids).order_by("voucher__date", "id")
                for purchase_row in purchase_voucher_rows:
                    can_be_added = purchase_row.quantity - purchase_row.remaining_quantity
                    diff = quantity - can_be_added
                    if diff >= can_be_added:
                        purchase_row.remaining_quantity += can_be_added
                        purchase_row.save()
                        row.sold_items[str(purchase_row.id)] -= can_be_added
                        quantity -= can_be_added
                        row.save()
                        break
                    else:
                        purchase_row.remaining_quantity += can_be_added
                        purchase_row.save()
                        quantity -= can_be_added
                        row.sold_items.pop(str(purchase_row.id))
                        row.save()
                        continue
                if ob and quantity>0:
                    inv_account = row.item.account
                    if quantity > ob:
                        inv_account.opening_balance = ob
                        quantity -= ob
                        inv_account.save()
                        row.save()
                    else:
                        inv_account.opening_balance = quantity
                        inv_account.save()
                        row.sold_items["OB"] = ob - quantity
                        row.save()
                        return

    def create(self, validated_data):
        from copy import deepcopy
        rows_data = validated_data.pop('rows')
        rows_data_copy = deepcopy(rows_data)
        invoices = validated_data.pop('invoices')
        request = self.context['request']
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        instance = CreditNote.objects.create(**validated_data)
        # sales_row_ids = []
        for index, row in enumerate(rows_data):
            row.pop("id")
            row = self.assign_discount_obj(row)
            CreditNoteRow.objects.create(voucher=instance, **row)
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.apply_transactions()
        if self.context["request"].company.inventory_setting.enable_fifo:
            self.cancel_sales(instance, rows_data_copy)
        # instance.synchronize()
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        invoices = validated_data.pop('invoices')
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        CreditNote.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            CreditNoteRow.objects.update_or_create(voucher=instance, pk=row.get('id'), defaults=row)
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.refresh_from_db()
        instance.apply_transactions()
        # instance.synchronize()
        return instance

    class Meta:
        model = CreditNote
        exclude = ('company', 'user', 'bank_account', 'discount_obj', 'fiscal_year',)


class CreditNoteListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = CreditNote
        fields = ('id', 'voucher_no', 'party', 'date', 'status',)


class CreditNoteDetailSerializer(serializers.ModelSerializer):
    party_name = serializers.ReadOnlyField(source='party.name')
    bank_account_name = serializers.ReadOnlyField(source='bank_account.friendly_name')
    discount_obj = SalesDiscountSerializer()
    voucher_meta = serializers.ReadOnlyField(source='get_voucher_meta')
    address = serializers.ReadOnlyField(source='party.address')

    rows = SalesVoucherRowDetailSerializer(many=True)
    tax_registration_number = serializers.ReadOnlyField(source='party.tax_registration_number')

    invoice_data = serializers.SerializerMethodField()
    # invoices = serializers.SerializerMethodField()

    # def get_invoices(self, obj):
    #     return obj.invoices.values_list("id", flat=True)

    def get_invoice_data(self, obj):
        data = []
        for invoice in obj.invoices.all():
            data.append({'id': invoice.id, 'voucher_no': invoice.voucher_no})
        return data

    class Meta:
        model = CreditNote
        exclude = ('company', 'user', 'bank_account')
