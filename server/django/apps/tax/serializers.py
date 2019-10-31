from rest_framework import serializers

from apps.ledger.serializers import AccountBalanceSerializer, TransactionSerializer, JournalEntrySerializer
from apps.tax.models import TaxScheme, TaxPayment


class TaxSchemeSerializer(serializers.ModelSerializer):
    default = serializers.ReadOnlyField()
    friendly_name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = TaxScheme
        exclude = ('company',)


class TaxAccountSerializer(serializers.ModelSerializer):
    payable = AccountBalanceSerializer()
    receivable = AccountBalanceSerializer()

    class Meta:
        model = TaxScheme
        fields = ('id', 'name', 'payable', 'receivable', 'recoverable')


class TaxSchemeMinSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = TaxScheme
        fields = ('id', 'name', 'rate')


class TaxPaymentSerializer(serializers.ModelSerializer):
    cr_account_name = serializers.ReadOnlyField(source="cr_account.name")
    tax_scheme_name = serializers.ReadOnlyField(source='tax_scheme.__str__')

    class Meta:
        model = TaxPayment
        exclude = ('company',)


class TaxPaymentJournalEntrySerializer(JournalEntrySerializer):
    transactions = serializers.SerializerMethodField()

    def get_transactions(self, obj):
        transactions = obj.transactions.all()
        return TransactionSerializer(transactions, many=True).data
