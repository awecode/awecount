from rest_framework import serializers

from apps.tax.models import TaxScheme, TaxPayment


class TaxSchemeSerializer(serializers.ModelSerializer):
    default = serializers.ReadOnlyField()
    friendly_name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = TaxScheme
        exclude = ('company',)


class TaxSchemeMinSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = TaxScheme
        fields = ('id', 'name', 'rate')


class TaxPaymentSerializer(serializers.ModelSerializer):
    cr_account_name = serializers.ReadOnlyField(source="cr_account.name")
    tax_scheme_name = serializers.ReadOnlyField(source='tax_scheme.short_name')

    class Meta:
        model = TaxPayment
        exclude = ('company',)
