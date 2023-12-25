from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.models import Account
from apps.ledger.serializers import AccountBalanceSerializer
from apps.tax.serializers import TaxSchemeSerializer
from awecount.libs.Base64FileField import Base64FileField
from awecount.libs.CustomViewSet import GenericSerializer
from .models import InventorySetting, Item, Unit, Category as InventoryCategory, Brand, InventoryAccount, JournalEntry, Category, \
    Transaction


class ItemSerializer(serializers.ModelSerializer):
    tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    unit_id = serializers.IntegerField(required=False, allow_null=True)
    extra_fields = serializers.ReadOnlyField(source='category.extra_fields')
    front_image = Base64FileField(required=False, allow_null=True)
    back_image = Base64FileField(required=False, allow_null=True)

    def validate_cost_price(self, attr):
        if attr and attr<0:
            raise ValidationError("Cost price cannot be negative.")
        return attr
    
    def validate_selling_price(self, attr):
        if attr and attr<0:
            raise ValidationError("Selling price cannot be negative.")
        return attr

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


class ItemOpeningSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='item.name')
    item_id = serializers.ReadOnlyField(source='item.id')

    class Meta:
        model = InventoryAccount
        fields = ('id', 'name', 'item_id', 'opening_balance',)


class ItemPOSSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField(source='selling_price')

    class Meta:
        model = Item
        fields = ('id', 'name', 'unit_id', 'rate', 'tax_scheme_id', 'code')


class ItemPurchaseSerializer(serializers.ModelSerializer):
    rate = serializers.ReadOnlyField(source='cost_price')
    is_trackable = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = ('id', 'name', 'unit_id', 'rate', 'tax_scheme_id', 'description', 'is_trackable', 'track_inventory')


class BookSerializer(ItemSerializer):
    def create(self, validated_data):
        request = self.context['request']
        category = Category.objects.filter(name="Book", company=request.user.company).first()
        if not category:
            raise ValidationError({'detail': 'Please create "Book" category first!'})
        validated_data['category'] = category

        if category.items_purchase_account_type == 'global':
            validated_data['purchase_account'] = Account.objects.get(name="Purchase Account", default=True)

        if category.items_sales_account_type == 'global':
            validated_data['sales_account'] = Account.objects.get(name="Sales Account", default=True)

        if category.items_discount_allowed_account_type == 'global':
            validated_data['discount_allowed_account'] = Account.objects.get(name="Discount Expenses", default=True)

        if category.items_discount_received_account_type == 'global':
            validated_data['discount_received_account'] = Account.objects.get(name="Discount Income", default=True)

        instance = super(BookSerializer, self).create(validated_data)
        return instance


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        exclude = ('company',)


class InventoryCategorySerializer(serializers.ModelSerializer):
    default_unit_id = serializers.IntegerField(required=False, allow_null=True)
    default_tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = InventoryCategory
        exclude = ('company', 'default_unit', 'default_tax_scheme', 'sales_account_category', 'purchase_account_category',
                   'discount_allowed_account_category', 'discount_received_account_category', 'fixed_asset_account_category',
                   'direct_expense_account_category', 'indirect_expense_account_category')


class InventoryCategoryTrialBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = ('name', 'id', 'can_be_sold', 'can_be_purchased', 'fixed_asset')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ('company',)


class InventoryAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAccount
        fields = ('account_no', 'code', 'current_balance', 'id', 'name', 'opening_balance', 'item')


class InventoryAccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAccount
        fields = ('id', 'amounts')


class ItemDetailSerializer(serializers.ModelSerializer):
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
        exclude = ('company',)


class ItemListSerializer(serializers.ModelSerializer):
    category = GenericSerializer()

    class Meta:
        model = Item
        fields = ('id', 'name', 'category', 'cost_price', 'selling_price', 'code')


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


class TransactionEntrySerializer(serializers.ModelSerializer):
    date = serializers.ReadOnlyField(source='journal_entry.date')
    source_type = serializers.SerializerMethodField()
    source_id = serializers.ReadOnlyField(source='journal_entry.source.get_source_id')

    # voucher_no is too expensive on DB -
    voucher_no = serializers.ReadOnlyField(source='journal_entry.source.get_voucher_no')

    def get_source_type(self, obj):
        v_type = obj.journal_entry.content_type.name
        if v_type[-4:] == ' row':
            v_type = v_type[:-3]
        if v_type[-11:] == ' particular':
            v_type = v_type[:-10]
        if v_type == 'account':
            return 'Opening Balance'
        return v_type.strip().title()

    class Meta:
        model = Transaction
        fields = (
            'id', 'dr_amount', 'cr_amount', 'current_balance', 'date', 'source_type', 'account_id', 'source_id',
            'voucher_no')


class InventorySettingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySetting
        exclude = ['company']