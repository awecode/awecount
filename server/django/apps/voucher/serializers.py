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


class SalesVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    unit_id = serializers.IntegerField(source='unit.id', required=False)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)
    show_description = serializers.SerializerMethodField()
    show_discount = serializers.SerializerMethodField()

    def get_show_discount(self, obj):
        return bool(obj.discount > 0)

    def get_show_description(self, obj):
        return bool(obj.description)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit',)


class SalesVoucherCreateSerializer(serializers.ModelSerializer):
    rows = SalesVoucherRowSerializer(many=True)
    voucher_discount = serializers.SerializerMethodField()
    company_id = serializers.IntegerField()
    bank_account_id = serializers.IntegerField(required=False, allow_null=True)

    def get_voucher_discount(self, obj):
        return obj.discount and obj.discount_type

    def validate(self, data):
        if not data.get('party') and not data.get('customer_name'):
            raise ValidationError(
                {'party': ['Either party or customer name is required']},
            )
        if not data.get('mode') == 'ePayment':
            data['epayment'] = ''
        if not data.get('mode') == 'Bank Deposit':
            data['bank_account_id'] = None
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        user_id = request.user.id
        validated_data['user_id'] = user_id
        voucher = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            SalesVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        SalesVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
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
            SalesVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        SalesVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = SalesVoucher
        exclude = ('company', 'user', 'bank_account',)


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


class PurchaseVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    unit_id = serializers.IntegerField(source='unit.id', required=False)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)
    show_description = serializers.SerializerMethodField()
    show_discount = serializers.SerializerMethodField()

    def get_show_discount(self, obj):
        return bool(obj.discount > 0)

    def get_show_description(self, obj):
        return bool(obj.description)

    class Meta:
        model = PurchaseVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit',)


class PurchaseVoucherCreateSerializer(serializers.ModelSerializer):
    rows = PurchaseVoucherRowSerializer(many=True)
    voucher_discount = serializers.SerializerMethodField()
    company_id = serializers.IntegerField()

    def get_voucher_discount(self, obj):
        return obj.discount and obj.discount_type

    def validate(self, data):
        if not data.get('party'):
            raise ValidationError(
                {'party': ['Party is required']},
            )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        voucher = PurchaseVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            PurchaseVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        # SalesVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
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
        # SalesVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = PurchaseVoucher
        exclude = ('company',)


class PurchaseVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}'.format(obj.voucher_no)

    class Meta:
        model = PurchaseVoucher
        fields = ('id', 'voucher_no', 'party', 'date', 'pending_amount', 'name',)


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
