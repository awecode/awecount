from rest_framework import serializers

from apps.ledger.serializers import (
    AccountBalanceSerializer,
    JournalEntrySerializer,
    TransactionSerializer,
    AccountMinSerializer,
)
from apps.tax.models import TaxPayment, TaxScheme


class TaxSchemeSerializer(serializers.ModelSerializer):
    default = serializers.ReadOnlyField()
    friendly_name = serializers.ReadOnlyField(source="__str__")

    class Meta:
        model = TaxScheme
        exclude = ("company",)


class TaxAccountSerializer(serializers.ModelSerializer):
    payable = AccountBalanceSerializer()
    receivable = AccountBalanceSerializer()

    class Meta:
        model = TaxScheme
        fields = ("id", "name", "payable", "receivable", "recoverable")


class TaxSchemeMinSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="__str__")

    class Meta:
        model = TaxScheme
        fields = ("id", "name", "rate")


class TaxPaymentSerializer(serializers.ModelSerializer):
    cr_account_name = serializers.ReadOnlyField(source="cr_account.name")
    tax_scheme_name = serializers.ReadOnlyField(source="tax_scheme.friendly_name")

    class Meta:
        model = TaxPayment
        exclude = ("company",)

class TaxPaymentFormSerializer(TaxPaymentSerializer):
    selected_cr_account_obj = AccountMinSerializer(read_only=True, source="cr_account")

class TaxPaymentJournalEntrySerializer(JournalEntrySerializer):
    transactions = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        transactions = obj.transactions.all()
        return TransactionSerializer(transactions, many=True).data
