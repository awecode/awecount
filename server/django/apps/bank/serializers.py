from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from awecount.libs.serializers import StatusReversionMixin
from .models import BankAccount, ChequeDeposit, ChequeIssue, BankCashDeposit, FundTransfer, FundTransferTemplate


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

    def validate_voucher_no(self, attr):
        if attr and attr > 214748364:
            raise ValidationError("Voucher Number should be a number between 0 to 214748364.")

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
        fields = ('id', 'voucher_no', 'bank_account', 'date', 'bank_account_name', 'benefactor_name', 'deposited_by', 'status')


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


class FundTransferListSerializer(serializers.ModelSerializer):
    from_account_name = serializers.ReadOnlyField(source='from_account.name')
    to_account_name = serializers.ReadOnlyField(source='to_account.name')

    class Meta:
        model = FundTransfer
        fields = (
            'id', 'voucher_no', 'date', 'from_account', 'to_account', 'from_account_name', 'to_account_name', 'amount', 'status')


class FundTransferTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTransferTemplate
        fields = ('id', 'name', 'from_account', 'to_account', 'transaction_fee_account', 'transaction_fee',)


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
        bank_cash_deposit.apply_transactions()
        return bank_cash_deposit

    def update(self, instance, validated_data):
        BankCashDeposit.objects.filter(pk=instance.id).update(**validated_data)
        if instance.status == 'Cleared':
            instance.refresh_from_db()
            instance.apply_transactions()
        return instance

    class Meta:
        model = BankCashDeposit
        exclude = ('company',)
