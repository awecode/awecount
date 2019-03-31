from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError
from apps.ledger.models import set_transactions as set_ledger_transaction

from .models import SalesVoucherRow, SalesVoucher, CreditVoucherRow, CreditVoucher, ChequeVoucher, BankBranch, \
    InvoiceDesign, BankAccount


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
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)
    show_description = serializers.SerializerMethodField()
    show_discount = serializers.SerializerMethodField()

    def get_show_discount(self, obj):
        return bool(obj.discount > 0)

    def get_show_description(self, obj):
        return bool(obj.description)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher')


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
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            SalesVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        SalesVoucher.apply_transactions(voucher)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['voucher'] = instance
            row['item_id'] = item.get('id')
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
        cash_receipt = CreditVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            CreditVoucherRow.objects.create(cash_receipt=cash_receipt, **row)
        cash_receipt.sale_vouchers.add(*sale_vouchers)
        return cash_receipt

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
                raise APIException({'errors': ['Voucher repeated in cash receipt.']})
        instance.sale_vouchers.clear()
        instance.sale_vouchers.add(*sale_vouchers)
        instance.refresh_from_db()
        return instance

    class Meta:
        model = CreditVoucher
        exclude = ('company',)


class CreditVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = CreditVoucher
        fields = ('id', 'voucher_no', 'party', 'date',)


class BankBranchSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = BankBranch
        fields = '__all__'


class ChequeVoucherSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    bank_branch_id = serializers.IntegerField(required=True)
    # party_id = serializers.IntegerField(source='party.id', required=False)
    company_id = serializers.IntegerField()
    payee = serializers.SerializerMethodField()
    party_name = serializers.ReadOnlyField(source='party.name')
    amount_in_words = serializers.SerializerMethodField()

    def get_amount_in_words(self, obj):
        return obj.amount_in_words

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        validated_data['user'] = user
        return super(ChequeVoucherSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        validated_data['user'] = user
        return super(ChequeVoucherSerializer, self).update(instance, validated_data)

    def get_name(self, obj):
        if obj.bank_branch:
            return obj.bank_branch.name

    def get_payee(self, obj):
        if obj.party:
            return obj.party.name
        return obj.customer_name

    class Meta:
        model = ChequeVoucher
        exclude = ('user', 'company',)


class InvoiceDesignSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = InvoiceDesign
        exclude = ('company',)


class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='account_number')
    company_id = serializers.IntegerField()

    class Meta:
        model = BankAccount
        exclude = ('company',)
