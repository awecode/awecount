from django.db.models import Count, F, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.ledger.serializers import AccountMinSerializer, PartyMinSerializer
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.serializers import StatusReversionMixin
from lib.drf.serializers import BaseModelSerializer

from .models import (
    BankAccount,
    BankCashDeposit,
    ChequeDeposit,
    ChequeIssue,
    FundTransfer,
    FundTransferTemplate,
    ReconciliationRow,
    ReconciliationStatement,
)


class BankAccountSerializer(BaseModelSerializer):
    name = serializers.ReadOnlyField(source="__str__")

    class Meta:
        model = BankAccount
        exclude = ("company",)


class BankAccountMinSerializer(BaseModelSerializer):
    name = serializers.ReadOnlyField(source="__str__")

    class Meta:
        model = BankAccount
        fields = ("id", "name")


class BankAccountWithLedgerSerializer(BaseModelSerializer):
    name = serializers.ReadOnlyField(source="__str__")
    cheque_no = serializers.ReadOnlyField(source="next_cheque_no")

    class Meta:
        model = BankAccount
        fields = ("id", "name", "ledger_id", "cheque_no", "account_number")


class ChequeDepositCreateSerializer(StatusReversionMixin, BaseModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    benefactor_name = serializers.ReadOnlyField(source="benefactor.name")
    # clearing_date = serializers.ReadOnlyField()
    voucher_no = serializers.IntegerField(required=False, allow_null=True)
    selected_bank_account_obj = GenericSerializer(read_only=True, source="bank_account")
    selected_benefactor_obj = GenericSerializer(read_only=True, source="benefactor")

    def validate_voucher_no(self, attr):
        if attr and attr > 214748364:
            raise ValidationError(
                "Voucher Number should be a number between 0 to 214748364."
            )
        return attr

    def create(self, validated_data):
        cheque_deposit = ChequeDeposit.objects.create(**validated_data)
        cheque_deposit.apply_transactions()
        return cheque_deposit

    def update(self, instance, validated_data):
        ChequeDeposit.objects.filter(pk=instance.id).update(**validated_data)
        if instance.status == "Cleared":
            instance.refresh_from_db()
            instance.apply_transactions()
        return instance

    class Meta:
        model = ChequeDeposit
        exclude = ("company",)


class ChequeDepositListSerializer(BaseModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source="bank_account.account_number")
    benefactor_name = serializers.ReadOnlyField(source="benefactor.name")

    class Meta:
        model = ChequeDeposit
        fields = (
            "id",
            "voucher_no",
            "bank_account",
            "date",
            "bank_account_name",
            "benefactor_name",
            "status",
        )


class BankCashDepositListSerializer(BaseModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source="bank_account.account_number")
    benefactor_name = serializers.ReadOnlyField(source="benefactor.name")

    class Meta:
        model = BankCashDeposit
        fields = (
            "id",
            "voucher_no",
            "bank_account",
            "date",
            "bank_account_name",
            "benefactor_name",
            "deposited_by",
            "status",
        )


class ChequeIssueSerializer(BaseModelSerializer):
    # party_id = serializers.IntegerField(source='party.id', required=False)
    payee = serializers.SerializerMethodField()
    party_name = serializers.ReadOnlyField(source="party.name")
    amount_in_words = serializers.SerializerMethodField()

    def get_amount_in_words(self, obj):
        return obj.amount_in_words

    def get_payee(self, obj):
        if obj.party:
            return obj.party.name
        return obj.issued_to

    class Meta:
        model = ChequeIssue
        exclude = ("company",)


class FundTransferSerializer(BaseModelSerializer):
    selected_from_account_obj = GenericSerializer(read_only=True, source="from_account")
    selected_to_account_obj = GenericSerializer(read_only=True, source="to_account")
    selected_transaction_fee_account_obj = GenericSerializer(
        read_only=True, source="transaction_fee_account"
    )

    class Meta:
        model = FundTransfer
        exclude = ("company",)


class FundTransferListSerializer(BaseModelSerializer):
    from_account_name = serializers.ReadOnlyField(source="from_account.name")
    to_account_name = serializers.ReadOnlyField(source="to_account.name")

    class Meta:
        model = FundTransfer
        fields = (
            "id",
            "voucher_no",
            "date",
            "from_account",
            "to_account",
            "from_account_name",
            "to_account_name",
            "amount",
            "status",
        )


class FundTransferTemplateSerializer(BaseModelSerializer):
    selected_from_account_obj = GenericSerializer(read_only=True, source="from_account")
    selected_to_account_obj = GenericSerializer(read_only=True, source="to_account")
    selected_transaction_fee_account_obj = GenericSerializer(
        read_only=True, source="transaction_fee_account"
    )

    class Meta:
        model = FundTransferTemplate
        fields = (
            "id",
            "name",
            "from_account",
            "to_account",
            "transaction_fee_account",
            "transaction_fee",
            "selected_from_account_obj",
            "selected_to_account_obj",
            "selected_transaction_fee_account_obj",
        )


class BankAccountChequeIssueSerializer(BaseModelSerializer):
    name = serializers.ReadOnlyField(source="__str__")
    cheque_no = serializers.ReadOnlyField(source="next_cheque_no")

    class Meta:
        model = BankAccount
        fields = (
            "id",
            "name",
            "account_number",
            "cheque_no",
        )


class ChequeIssueFormSerializer(ChequeIssueSerializer):
    selected_bank_account_obj = BankAccountChequeIssueSerializer(
        read_only=True, source="bank_account"
    )
    selected_party_obj = PartyMinSerializer(source="party", read_only=True)
    selected_dr_account_obj = GenericSerializer(source="dr_account", read_only=True)


class BankCashDepositCreateSerializer(StatusReversionMixin, BaseModelSerializer):
    bank_account_name = serializers.ReadOnlyField(source="bank_account.friendly_name")
    benefactor_name = serializers.ReadOnlyField(source="benefactor.name")
    voucher_no = serializers.IntegerField(required=False, allow_null=True)
    selected_bank_account_obj = GenericSerializer(read_only=True, source="bank_account")
    selected_benefactor_obj = GenericSerializer(read_only=True, source="benefactor")

    def create(self, validated_data):
        bank_cash_deposit = BankCashDeposit.objects.create(**validated_data)
        bank_cash_deposit.apply_transactions()
        return bank_cash_deposit

    def update(self, instance, validated_data):
        BankCashDeposit.objects.filter(pk=instance.id).update(**validated_data)
        if instance.status == "Cleared":
            instance.refresh_from_db()
            instance.apply_transactions()
        return instance

    class Meta:
        model = BankCashDeposit
        exclude = ("company",)


class ReconciliationRowSerializer(BaseModelSerializer):
    class Meta:
        model = ReconciliationRow
        exclude = ("updated_at", "statement")


class ReconciliationStatementImportSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    transactions = serializers.ListField(child=serializers.DictField())
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    merge_description = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            "account_id",
            "transactions",
            "start_date",
            "end_date",
            "merge_description",
        )


class ReconciliationStatementListSerializer(BaseModelSerializer):
    account = AccountMinSerializer()
    total_rows = serializers.SerializerMethodField()
    reconciled_rows = serializers.SerializerMethodField()
    has_updated_rows = serializers.SerializerMethodField()

    def get_total_rows(self, obj):
        return obj.rows.count()

    def get_reconciled_rows(self, obj):
        return obj.rows.filter(status="Reconciled").count()

    def get_has_updated_rows(self, obj):
        # find if there are any rows that have been updated
        return (
            obj.rows.annotate(transaction_count=Count("transactions"))
            .filter(
                Q(transaction_count__gt=0) & Q(transactions__transaction__isnull=True)
                | Q(
                    transactions__transaction_last_updated_at__lt=F(
                        "transactions__transaction__updated_at"
                    )
                )
            )
            .exists()
        )

    class Meta:
        model = ReconciliationStatement
        fields = (
            "id",
            "account",
            "start_date",
            "end_date",
            "total_rows",
            "reconciled_rows",
            "has_updated_rows",
        )


class ReconciliationStatementSerializer(BaseModelSerializer):
    account = AccountMinSerializer()
    entries = ReconciliationRowSerializer(many=True)

    class Meta:
        model = ReconciliationStatement
        fields = ("id", "account", "start_date", "end_date", "entries")
