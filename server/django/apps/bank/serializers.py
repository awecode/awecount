from rest_framework import serializers

from .models import BankAccount, ChequeDepositRow, ChequeDeposit


class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='account_number')
    company_id = serializers.IntegerField()

    class Meta:
        model = BankAccount
        exclude = ('company',)


class ChequeDepositRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ChequeDepositRow
        exclude = ('cheque_deposit',)


class ChequeDepositCreateSerializer(serializers.ModelSerializer):
    rows = ChequeDepositRowSerializer(many=True)
    company_id = serializers.IntegerField()

    # bank_account_id = serializers.IntegerField(required=False, allow_null=True)
    # benefactor_id = serializers.IntegerField(required=False, allow_null=True)

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
        # exclude = ('company', 'benefactor', 'bank_account',)
        exclude = ('company',)


class ChequeDepositListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{}: {}'.format(obj.voucher_no, obj.deposited_by)

    class Meta:
        model = ChequeDeposit
        fields = ('id', 'voucher_no', 'bank_account', 'date', 'deposited_by', 'name')
