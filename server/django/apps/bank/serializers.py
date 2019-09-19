from rest_framework import serializers

from awecount.utils.serializers import StatusReversionMixin
from .models import BankAccount, ChequeDepositRow, ChequeDeposit, ChequeIssue


class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = BankAccount
        exclude = ('company',)


class ChequeDepositRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ChequeDepositRow
        exclude = ('cheque_deposit',)


class ChequeDepositCreateSerializer(StatusReversionMixin, serializers.ModelSerializer):
    rows = ChequeDepositRowSerializer(many=True)
    bank_account_name = serializers.ReadOnlyField(source='bank_account.name')
    benefactor_name = serializers.ReadOnlyField(source='bank_account.name')
    voucher_no = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        cheque_deposit = ChequeDeposit.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            ChequeDepositRow.objects.create(cheque_deposit=cheque_deposit, **row)
        # ChequeDeposit.apply_transactions(voucher)
        return cheque_deposit

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        ChequeDeposit.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row['cheque_deposit'] = instance
            ChequeDepositRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        # ChequeDeposit.apply_transactions(instance)
        return instance

    class Meta:
        model = ChequeDeposit
        exclude = ('company', 'clearing_date',)


class ChequeDepositListSerializer(serializers.ModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source='bank_account.account_number')
    benefactor_name = serializers.ReadOnlyField(source='benefactor.name')

    class Meta:
        model = ChequeDeposit
        fields = ('id', 'voucher_no', 'bank_account', 'date', 'bank_account_name', 'benefactor_name')


class ChequeIssueSerializer(serializers.ModelSerializer):
    # party_id = serializers.IntegerField(source='party.id', required=False)
    payee = serializers.SerializerMethodField()
    party_name = serializers.ReadOnlyField(source='party.name')
    amount_in_words = serializers.SerializerMethodField()

    def get_amount_in_words(self, obj):
        return obj.amount_in_words

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        validated_data['user'] = user
        return super(ChequeIssueSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        validated_data['user'] = user
        return super(ChequeIssueSerializer, self).update(instance, validated_data)

    def get_payee(self, obj):
        if obj.party:
            return obj.party.name
        return obj.customer_name

    class Meta:
        model = ChequeIssue
        exclude = ('user', 'company',)


class BankAccountChequeVoucherSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='__str__')
    cheque_no = serializers.ReadOnlyField(source='get_cheque_no')

    class Meta:
        model = BankAccount
        fields = ('id', 'name', 'account_number', 'cheque_no',)
