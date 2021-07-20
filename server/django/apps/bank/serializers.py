from rest_framework import serializers

from awecount.utils.serializers import StatusReversionMixin
from .models import BankAccount, ChequeDeposit, ChequeIssue, BankCashDeposit, FundTransfer


class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = BankAccount
        exclude = ('company',)


class ChequeDepositCreateSerializer(StatusReversionMixin, serializers.ModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source='bank_account.friendly_name')
    benefactor_name = serializers.ReadOnlyField(source='benefactor.name')
    # clearing_date = serializers.ReadOnlyField()
    voucher_no = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        cheque_deposit = ChequeDeposit.objects.create(**validated_data)
        cheque_deposit.apply_transactions()
        return cheque_deposit

    def update(self, instance, validated_data):
        ChequeDeposit.objects.filter(pk=instance.id).update(**validated_data)
        if instance.status == 'Cleared':
            instance.refresh_from_db()
            instance.apply_transactions()
        return instance

    class Meta:
        model = ChequeDeposit
        exclude = ('company',)


class ChequeDepositListSerializer(serializers.ModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source='bank_account.account_number')
    benefactor_name = serializers.ReadOnlyField(source='benefactor.name')

    class Meta:
        model = ChequeDeposit
        fields = ('id', 'voucher_no', 'bank_account', 'date', 'bank_account_name', 'benefactor_name', 'status')


class BankCashDepositListSerializer(serializers.ModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source='bank_account.account_number')
    benefactor_name = serializers.ReadOnlyField(source='benefactor.name')

    class Meta:
        model = BankCashDeposit
        fields = ('id', 'voucher_no', 'bank_account', 'date', 'bank_account_name', 'benefactor_name', 'deposited_by',)


class ChequeIssueSerializer(serializers.ModelSerializer):
    # party_id = serializers.IntegerField(source='party.id', required=False)
    payee = serializers.SerializerMethodField()
    party_name = serializers.ReadOnlyField(source='party.name')
    amount_in_words = serializers.SerializerMethodField()

    def get_amount_in_words(self, obj):
        return obj.amount_in_words

    def get_payee(self, obj):
        if obj.party:
            return obj.party.name
        return obj.issued_to

    class Meta:
        model = ChequeIssue
        exclude = ('company',)


class FundTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTransfer
        exclude = ('company',)


class BankAccountChequeIssueSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='__str__')
    cheque_no = serializers.ReadOnlyField(source='next_cheque_no')

    class Meta:
        model = BankAccount
        fields = ('id', 'name', 'account_number', 'cheque_no',)


class BankCashDepositCreateSerializer(StatusReversionMixin, serializers.ModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source='bank_account.friendly_name')
    benefactor_name = serializers.ReadOnlyField(source='benefactor.name')
    voucher_no = serializers.IntegerField(required=False, allow_null=True)

    def create(self, validated_data):
        bank_cash_deposit = BankCashDeposit.objects.create(**validated_data)
        # cheque_deposit.apply_transactions()
        return bank_cash_deposit

    def update(self, instance, validated_data):
        BankCashDeposit.objects.filter(pk=instance.id).update(**validated_data)
        # if instance.status == 'Cleared':
        #     instance.refresh_from_db()
        #     instance.apply_transactions()
        return instance

    class Meta:
        model = BankCashDeposit
        exclude = ('company',)
