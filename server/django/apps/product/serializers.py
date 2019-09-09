from django.core.files.base import ContentFile
from rest_framework import serializers

from apps.ledger.models import Account
from apps.ledger.serializers import AccountSerializer
from apps.tax.serializers import TaxSchemeSerializer
from awecount.utils.Base64FileField import Base64FileField
from .models import Item, Unit, Category as InventoryCategory, Brand, InventoryAccount, JournalEntry, Category


class ItemSerializer(serializers.ModelSerializer):
    tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    unit_id = serializers.IntegerField(required=False)
    extra_fields = serializers.ReadOnlyField(source='category.extra_fields')
    front_image = Base64FileField(required=False, allow_null=True)
    back_image = Base64FileField(required=False, allow_null=True)

    @staticmethod
    def base64_check(validated_data, attributes):
        for attr in attributes:
            if validated_data.get(attr) and not isinstance(validated_data.get(attr),
                                                           ContentFile):
                validated_data.pop(attr)
        return validated_data

    def update(self, instance, validated_data):
        validated_data = self.base64_check(validated_data, ['front_image', 'back_image'])
        return super().update(instance, validated_data)

    class Meta:
        model = Item
        exclude = ('company', 'tax_scheme', 'unit',)


class ItemSalesSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField(source='selling_price')
    is_trackable = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = ('id', 'name', 'unit_id', 'rate', 'tax_scheme_id', 'code', 'description', 'is_trackable')


class ItemPurchaseSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField(source='cost_price')
    is_trackable = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = ('id', 'name', 'unit_id', 'rate', 'tax_scheme_id', 'description', 'is_trackable')


class BookSerializer(ItemSerializer):
    def create(self, validated_data):
        request = self.context['request']
        category = Category.objects.filter(name="Book", company=request.user.company)[0]
        validated_data['category'] = category

        if category.items_purchase_ledger_type == 'global':
            validated_data['purchase_ledger'] = Account.objects.get(name="Purchase Account", default=True)

        if category.items_sales_ledger_type == 'global':
            validated_data['sales_ledger'] = Account.objects.get(name="Sales Account", default=True)

        if category.items_discount_allowed_ledger_type == 'global':
            validated_data['discount_allowed_ledger'] = Account.objects.get(name="Discount Expenses", default=True)

        if category.items_discount_received_ledger_type == 'global':
            validated_data['discount_received_ledger'] = Account.objects.get(name="Discount Income", default=True)

        instance = super(BookSerializer, self).create(validated_data)
        return instance


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        exclude = ('company',)


class InventoryCategorySerializer(serializers.ModelSerializer):
    default_unit_id = serializers.IntegerField(required=False)
    default_tax_scheme_id = serializers.IntegerField(required=False)

    class Meta:
        model = InventoryCategory
        exclude = ('company', 'default_unit', 'default_tax_scheme')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ('company',)


class InventoryAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAccount
        fields = '__all__'


class ItemDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = InventoryCategorySerializer()
    unit = UnitSerializer()
    account = InventoryAccountSerializer()

    discount_allowed_ledger = AccountSerializer()
    discount_received_ledger = AccountSerializer()

    sales_ledger = AccountSerializer()
    purchase_ledger = AccountSerializer()
    tax_scheme = TaxSchemeSerializer()

    class Meta:
        model = Item
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    dr_amount = serializers.SerializerMethodField()
    cr_amount = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    voucher_type = serializers.SerializerMethodField()
    voucher_no = serializers.ReadOnlyField(source='source.get_voucher_no')
    source_id = serializers.ReadOnlyField(source='source.get_source_id')

    def get_voucher_type(self, obj):
        v_type = obj.content_type.name
        if v_type[-4:] == ' row':
            v_type = v_type[:-3]
        if v_type[-11:] == ' particular':
            v_type = v_type[:-10]
        if v_type == 'account':
            return 'Opening Balance'
        return v_type.title()

    def transaction(self, obj):
        account = self.context.get('account', None)
        try:
            transactions = [transaction for transaction in obj.transactions.all() if
                            transaction.account.id == account.id]
            if transactions:
                return transactions[0]
        except Exception as e:
            return

    def get_dr_amount(self, obj):
        amount = '-'
        transaction = self.transaction(obj)
        if transaction:
            amount = transaction.dr_amount
        return amount

    def get_cr_amount(self, obj):
        amount = '-'
        transaction = self.transaction(obj)
        if transaction:
            amount = transaction.cr_amount
        return amount

    def get_balance(self, obj):
        amount = '-'
        transaction = self.transaction(obj)
        if transaction:
            amount = transaction.get_balance()
        return amount

    class Meta:
        model = JournalEntry
        fields = '__all__'
