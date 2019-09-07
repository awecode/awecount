from rest_framework import serializers

from apps.tax.models import TaxScheme


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
