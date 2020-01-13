from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from awecount.libs.drf_fields import RoundedField
from .models import Party, Account, JournalEntry, PartyRepresentative, Category, Transaction


class PartyRepresentativeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PartyRepresentative
        exclude = ('party',)


class PartyMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('id', 'name', 'address', 'tax_registration_number')


class AccountSerializer(serializers.ModelSerializer):
    current_dr = RoundedField()
    current_cr = RoundedField()

    class Meta:
        model = Account
        exclude = ('company', 'default')


class AccountBalanceSerializer(serializers.ModelSerializer):
    current_dr = RoundedField()
    current_cr = RoundedField()

    class Meta:
        model = Account
        fields = ('id', 'code', 'current_dr', 'current_cr', 'balance')


class PartyAccountSerializer(serializers.ModelSerializer):
    supplier_account = AccountBalanceSerializer()
    customer_account = AccountBalanceSerializer()

    class Meta:
        model = Party
        fields = ('id', 'name', 'tax_registration_number', 'supplier_account', 'customer_account')


class PartySerializer(serializers.ModelSerializer):
    representative = PartyRepresentativeSerializer(many=True)

    def create(self, validated_data):
        representatives = validated_data.pop('representative', None)
        instance = super().create(validated_data)
        for representative in representatives:
            representative['party_id'] = instance.id
            PartyRepresentative.objects.create(**representative)
        return instance

    def update(self, instance, validated_data):
        representatives = validated_data.pop('representative', None)
        instance = super().update(instance, validated_data)
        # Party.objects.filter(pk=instance.id).update(**validated_data)
        for index, representative in enumerate(representatives):
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


class TransactionEntrySerializer(serializers.ModelSerializer):
    date = serializers.ReadOnlyField(source='journal_entry.date')
    source_type = serializers.SerializerMethodField()
    source_id = serializers.ReadOnlyField(source='journal_entry.source.get_source_id')
    current_dr = RoundedField()
    current_cr = RoundedField()
    dr_amount = RoundedField()
    cr_amount = RoundedField()

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
            'id', 'dr_amount', 'cr_amount', 'current_dr', 'current_cr', 'date', 'source_type', 'account_id', 'source_id',
            'voucher_no')


class RecursiveField(serializers.Serializer):
    def to_native(self, value):
        return CategorySerializer(value, context={"parent": self.parent.object, "parent_serializer": self.parent})


class CategorySerializer(serializers.ModelSerializer):
    # parent = RecursiveField(many=True, read_only=True)
    is_default = serializers.ReadOnlyField()

    class Meta:
        model = Category
        exclude = ('company',)


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
    current_dr = RoundedField()
    current_cr = RoundedField()

    def get_journal_entries(self, obj):
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()
        return JournalEntrySerializer(entries, context={'account': obj}, many=True).data

    class Meta:
        model = Account
        fields = (
            'id', 'code', 'closing_balance', 'name', 'current_dr', 'current_cr', 'opening_dr', 'opening_cr',
            'category_name',
            'parent_name', 'category_id', 'parent_id')


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']
