from rest_framework import serializers

from apps.tax.models import TaxScheme


class TaxSchemeSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = TaxScheme
        exclude = ('company',)
