from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError

from .models import SalesVoucherRow, SalesVoucher, CreditVoucherRow, CreditVoucher, InvoiceDesign, JournalVoucher, \
    JournalVoucherRow, PurchaseVoucher, \
    PurchaseVoucherRow, SalesDiscount, PurchaseDiscount


class SaleVoucherRowCreditNoteOptionsSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    discount = serializers.ReadOnlyField(source='discount_amount')
    credit_amount = serializers.ReadOnlyField(source='total')

    class Meta:
        model = SalesVoucherRow
        fields = ('item_id', 'tax_scheme_id', 'discount', 'credit_amount',)


# Serializer mixins need to inherit from serializers.Serializer
class DiscountObjectTypeSerializerMixin(serializers.Serializer):
    discount_type = serializers.CharField(required=False, allow_null=True)

    def assign_discount_obj(self, validated_data):
        discount_key = validated_data.get('discount_type')
        if discount_key and str(discount_key).isdigit():
            validated_data['discount_obj_id'] = discount_key
            validated_data['discount'] = 0
            validated_data['discount_type'] = None
        else:
            validated_data['discount_obj_id'] = None
        return validated_data

    def to_representation(self, obj):
        if obj.discount_obj_id:
            self.fields['discount_type'] = serializers.IntegerField(source='discount_obj_id')
        else:
            self.fields['discount_type'] = serializers.CharField()
        return super().to_representation(obj)


class ModeCumBankSerializerMixin(serializers.Serializer):
    mode = serializers.CharField(required=True)
    bank_account_id = serializers.IntegerField(required=False, allow_null=True)

    def assign_mode(self, validated_data):
        mode = validated_data.get('mode')
        if mode and str(mode).isdigit():
            validated_data['bank_account_id'] = mode
            validated_data['mode'] = 'Bank Deposit'
        else:
            validated_data['bank_account_id'] = None
        return validated_data

    def to_representation(self, obj):
        if obj.mode == 'Bank Deposit' and obj.bank_account_id:
            self.fields['mode'] = serializers.IntegerField(source='bank_account_id')
        return super().to_representation(obj)


class SalesVoucherRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    unit_id = serializers.IntegerField(source='unit.id', required=False)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit',)


class SalesVoucherCreateSerializer(DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin, serializers.ModelSerializer):
    rows = SalesVoucherRowSerializer(many=True)

    def validate(self, data):
        if not data.get('party') and data.get('mode') == 'Credit' and data.get('status') != 'Draft':
            raise ValidationError(
                {'party': ['Party is required for a credit issue.']},
            )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        validated_data = self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        voucher = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            row = self.assign_discount_obj(row)
            SalesVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        SalesVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        validated_data = self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            row['voucher'] = instance
            row['item_id'] = item.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            row = self.assign_discount_obj(row)
            SalesVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        SalesVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = SalesVoucher
        exclude = ('company', 'user', 'bank_account', 'discount_obj')


class PurchaseVoucherRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    unit_id = serializers.IntegerField(source='unit.id', required=False)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)

    class Meta:
        model = PurchaseVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit',)


class PurchaseVoucherCreateSerializer(DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin, serializers.ModelSerializer):
    rows = PurchaseVoucherRowSerializer(many=True)

    def validate(self, data):
        if not data.get('party') and data.get('mode') == 'Credit' and data.get('status') != 'Draft':
            raise ValidationError(
                {'party': ['Party is required for a credit issue.']},
            )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        validated_data = self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        voucher = PurchaseVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            PurchaseVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        PurchaseVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        validated_data = self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        PurchaseVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            row['voucher'] = instance
            row['item_id'] = item.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            PurchaseVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        PurchaseVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = PurchaseVoucher
        exclude = ('company', 'user', 'bank_account', 'discount_obj',)


class SalesVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}: {}'.format(obj.voucher_no, obj.user)

    class Meta:
        model = SalesVoucher
        fields = ('id', 'voucher_no', 'party', 'transaction_date', 'status', 'name',)


class SaleVoucherOptionsSerializer(serializers.ModelSerializer):
    value = serializers.ReadOnlyField(source='pk')
    text = serializers.ReadOnlyField(source='voucher_no')

    class Meta:
        model = SalesVoucher
        fields = ('value', 'text',)


class CreditVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    receipt = serializers.FloatField(required=False)
    # invoice_id = serializers.IntegerField(source='invoice.id', required=True)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    cash_receipt_id = serializers.IntegerField(source='cash_receipt.id', required=False, read_only=True)

    class Meta:
        model = CreditVoucherRow
        exclude = ('item', 'tax_scheme', 'cash_receipt',)


class CreditVoucherCreateSerializer(serializers.ModelSerializer):
    rows = CreditVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()
    sale_vouchers_options = serializers.SerializerMethodField(read_only=True)
    fetched_sale_vouchers = serializers.SerializerMethodField(read_only=True)

    def get_sale_vouchers_options(self, obj):
        sale_vouchers = obj.sale_vouchers.all()
        data = SaleVoucherOptionsSerializer(sale_vouchers, many=True).data
        return data

    def get_fetched_sale_vouchers(self, obj):
        data = [voucher.id for voucher in obj.sale_vouchers.all()]
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        sale_vouchers = validated_data.pop('sale_vouchers')
        credit_voucher = CreditVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            CreditVoucherRow.objects.create(cash_receipt=credit_voucher, **row)
        credit_voucher.sale_vouchers.add(*sale_vouchers)
        CreditVoucher.apply_transactions(credit_voucher)
        return credit_voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        sale_vouchers = validated_data.pop('sale_vouchers')
        CreditVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            row['cash_receipt'] = instance
            try:
                CreditVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
            except IntegrityError:
                raise APIException({'non_field_errors': ['Voucher repeated in cash receipt.']})
        instance.sale_vouchers.clear()
        instance.sale_vouchers.add(*sale_vouchers)
        instance.refresh_from_db()
        CreditVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = CreditVoucher
        exclude = ('company',)


class CreditVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = CreditVoucher
        fields = ('id', 'voucher_no', 'party', 'date',)


class InvoiceDesignSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = InvoiceDesign
        exclude = ('company',)


class JournalVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    account_id = serializers.IntegerField(source='account.id', required=True)
    journal_voucher_id = serializers.IntegerField(source='journal_voucher.id', required=False, read_only=True)
    show_description = serializers.SerializerMethodField()

    def get_show_description(self, obj):
        return bool(obj.description)

    class Meta:
        model = JournalVoucherRow
        exclude = ('account', 'journal_voucher',)


class JournalVoucherCreateSerializer(serializers.ModelSerializer):
    rows = JournalVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        journal_voucher = JournalVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop('account')
            row['account_id'] = account.get('id')
            JournalVoucherRow.objects.create(journal_voucher=journal_voucher, **row)
        JournalVoucher.apply_transactions(journal_voucher)
        return journal_voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        JournalVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop('account')
            row['account_id'] = account.get('id')
            row['journal_voucher'] = instance
            try:
                JournalVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
            except IntegrityError:
                raise APIException({'non_field_errors': ['Voucher repeated in journal voucher.']})
        instance.refresh_from_db()
        JournalVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = JournalVoucher
        exclude = ('company',)


class JournalVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalVoucher
        fields = ('id', 'voucher_no', 'date', 'status',)


class PurchaseVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}'.format(obj.voucher_no)

    class Meta:
        model = PurchaseVoucher
        fields = ('id', 'voucher_no', 'party', 'date', 'name',)


class SalesDiscountSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = SalesDiscount
        exclude = ('company',)


class PurchaseDiscountSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = PurchaseDiscount
        exclude = ('company',)
