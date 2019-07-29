from rest_framework import serializers

from .models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='account_number')
    company_id = serializers.IntegerField()

    class Meta:
        model = BankAccount
        exclude = ('company',)

