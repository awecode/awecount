from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import APIException
from apps.ledger.models.base import AccountClosing

from awecount.libs.drf_fields import RoundedField
from .models import Party, Account, JournalEntry, PartyRepresentative, Category, Transaction, AccountOpeningBalance


class PartyRepresentativeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PartyRepresentative
        exclude = ('party',)


class PartyMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('id', 'name', 'address', 'tax_registration_number')


class CategoryMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class AccountListSerializer(serializers.ModelSerializer):
    dr = RoundedField()
    cr = RoundedField()
    computed_balance = RoundedField()
    category = CategoryMinSerializer()

    class Meta:
        model = Account
        fields = ('id', 'code', 'name', 'dr', 'cr', 'computed_balance', 'category')


class AccountSerializer(serializers.ModelSerializer):
    # current_dr = RoundedField()
    # current_cr = RoundedField()

    class Meta:
        model = Account
        exclude = ('company', 'default')


class AccountFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'code', 'parent', 'category')


class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'code', 'amounts')


class PartyAccountSerializer(serializers.ModelSerializer):
    supplier_account = AccountBalanceSerializer()
    customer_account = AccountBalanceSerializer()

    class Meta:
        model = Party
        fields = ('id', 'name', 'tax_registration_number', 'supplier_account', 'customer_account')


class PartySerializer(serializers.ModelSerializer):
    tax_registration_number = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    representative = PartyRepresentativeSerializer(many=True, required=False)

    def create(self, validated_data):
        representatives = validated_data.pop('representative', None)
        if validated_data.get("tax_registration_number") == "":
            validated_data["tax_registration_number"] = None
        # else:
        #     validated_data["part"]
        instance = super().create(validated_data)
        if representatives:
            for representative in representatives:
                if representative.get('name') or representative.get('phone') or representative.get(
                        'email') or representative.get(
                    'position'):
                    representative['party_id'] = instance.id
                    PartyRepresentative.objects.create(**representative)
        return instance

    def update(self, instance, validated_data):
        representatives = validated_data.pop('representative', None)
        if validated_data.get("tax_registration_number") == "":
            validated_data["tax_registration_number"] = None
        instance = super().update(instance, validated_data)
        # Party.objects.filter(pk=instance.id).update(**validated_data)
        for index, representative in enumerate(representatives):
            if representative.get('name') or representative.get('phone') or representative.get(
                    'email') or representative.get(
                'position'):
                representative['party_id'] = instance.id
                try:
                    PartyRepresentative.objects.update_or_create(
                        pk=representative.get('id'),
                        defaults=representative
                    )
                except IntegrityError:
                    raise APIException({'detail': 'Party representative already created.'})
        return instance

    class Meta:
        model = Party
        exclude = ('company',)


class PartyListSerializer(serializers.ModelSerializer):
    dr = serializers.ReadOnlyField()
    cr = serializers.ReadOnlyField()
    balance = serializers.ReadOnlyField()

    class Meta:
        model = Party
        fields = (
            'id', 'name', 'address', 'contact_no', 'email', 'tax_registration_number', 'dr', 'cr', 'balance')


class CategorySerializer(serializers.ModelSerializer):
    is_default = serializers.ReadOnlyField()

    class Meta:
        model = Category
        exclude = ('company',)

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise ValidationError({"code": ["Category with this code already exists."]})

class AccountMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'code', 'default',)


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


class TransactionSerializer(serializers.ModelSerializer):
    account = AccountMinSerializer()

    class Meta:
        model = Transaction
        fields = "__all__"


class SalesJournalEntrySerializer(JournalEntrySerializer):
    transactions = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        transactions = obj.transactions.all()
        return TransactionSerializer(transactions, many=True).data


class JournalEntriesSerializer(JournalEntrySerializer):
    transactions = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        transactions = obj.transactions.all()
        return TransactionSerializer(transactions, many=True).data


class JournalEntryMultiAccountSerializer(serializers.ModelSerializer):
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
        account_ids = self.context.get('account_ids', None)
        try:
            transactions = [transaction for transaction in obj.transactions.all() if
                            transaction.account.id in account_ids]
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


class AccountDetailSerializer(serializers.ModelSerializer):
    # journal_entries = serializers.SerializerMethodField()
    closing_balance = serializers.ReadOnlyField(source='get_balance')
    category_name = serializers.ReadOnlyField(source='category.name')
    parent_name = serializers.ReadOnlyField(source='parent.name')

    def get_journal_entries(self, obj):
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()
        return JournalEntrySerializer(entries, context={'account': obj}, many=True).data

    class Meta:
        model = Account
        fields = (
            'id', 'code', 'closing_balance', 'name', 'amounts', 'opening_dr', 'opening_cr', 'category_name', 'amounts',
            'parent_name', 'category_id', 'parent_id')


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']


class AccountOpeningBalanceListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='account.name')

    class Meta:
        model = AccountOpeningBalance
        fields = ('id', 'name', 'opening_dr', 'opening_cr')


class AccountOpeningBalanceSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='account.name')
    class Meta:
        model = AccountOpeningBalance
        fields = ('id', 'account', 'name', 'opening_dr', 'opening_cr')


class TransactionEntrySerializer(serializers.Serializer):
    date = serializers.ReadOnlyField()
    source_type = serializers.SerializerMethodField()
    dr_amount = RoundedField(source='total_dr_amount')
    cr_amount = RoundedField(source='total_cr_amount')
    accounts = serializers.ReadOnlyField()
    source_id = serializers.ReadOnlyField()
    count = serializers.ReadOnlyField()
    voucher_no = serializers.ReadOnlyField()

    # voucher_no = serializers.ReadOnlyField(source='journal_entry.source_voucher_no')

    def get_source_type(self, obj):
        from django.apps import apps

        v_type = obj.content_type_model if obj.content_type_model else obj.journal_entry.content_type.model
        app_label = obj.content_type_app_label if obj.content_type_app_label else obj.journal_entry.content_type.app_label

        m = apps.get_model(app_label, v_type)
        if v_type[-4:] == ' row':
            v_type = v_type[:-3]
        if v_type[-11:] == ' particular':
            v_type = v_type[:-10]
        if v_type == 'account':
            return 'Opening Balance'
        return m._meta.verbose_name.title().replace('Row', '').strip()

    # class Meta:
    #     model = Transaction
    #     fields = ('source_id', 'count', 'source_type', 'date', 'dr_amount', 'cr_amount', 'account_names', 'account_ids')


class TransactionReportSerializer(serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField(source="journal_entry.source_voucher_no")
    date = serializers.ReadOnlyField(source="journal_entry.date")
    account = AccountMinSerializer()
    source_type = serializers.SerializerMethodField()
    account_name = serializers.ReadOnlyField(source="account.name")
    category_id = serializers.ReadOnlyField(source="account.category.id")

    def get_source_type(self, obj):
        from django.apps import apps

        v_type = obj.journal_entry.content_type.model
        m = apps.get_model(obj.journal_entry.content_type.app_label, v_type)

        if v_type[-4:] == ' row':
            v_type = v_type[:-3]
        if v_type[-11:] == ' particular':
            v_type = v_type[:-10]
        if v_type == 'account':
            return 'Opening Balance'
        return m._meta.verbose_name.title().replace('Row', '').strip()

    class Meta:
        model = Transaction
        fields = ["voucher_no", "date", "account", "source_type", "dr_amount", "cr_amount", "account_name", "category_id"]


class ContentTypeListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = ('id', 'name', 'model')

    def get_name(self, obj):
        return obj.name.capitalize()


class ParamSerializer(serializers.Serializer):
    account = serializers.ListField(child=serializers.IntegerField())


class AggregatorSerializer(serializers.Serializer):
    label = serializers.CharField(required=False)
    year = serializers.CharField(required=False)
    total_debit = RoundedField()
    total_credit = RoundedField()


class AccountClosingSerializer(serializers.ModelSerializer):
    # fiscal_period = serializers.StringRelatedField()
    company = serializers.StringRelatedField()

    class Meta:
        model = AccountClosing
        fields = ["company", "fiscal_period", "status"]
        extra_kwargs = {
            "status": {"read_only": True},
            "company": {"read_only": True}
        }
