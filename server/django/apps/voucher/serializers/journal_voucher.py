from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from ..models import JournalVoucherRow, JournalVoucher
from awecount.utils.serializers import StatusReversionMixin


class JournalVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    account_id = serializers.IntegerField(source='account.id', required=True)

    class Meta:
        model = JournalVoucherRow
        exclude = ('account', 'journal_voucher',)


class JournalVoucherCreateSerializer(StatusReversionMixin, serializers.ModelSerializer):
    rows = JournalVoucherRowSerializer(many=True)

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        validated_data['company_id'] = self.context['request'].company_id
        journal_voucher = JournalVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop('account')
            row['account_id'] = account.get('id')
            JournalVoucherRow.objects.create(journal_voucher=journal_voucher, **row)
        JournalVoucher.apply_transactions(journal_voucher)
        return journal_voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        validated_data['company_id'] = self.context['request'].company_id
        self.validate_voucher_status(validated_data, instance)
        JournalVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            account = row.pop('account')
            row['account_id'] = account.get('id')
            row['journal_voucher'] = instance
            try:
                JournalVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
            except IntegrityError:
                raise APIException({'non_field_errors': ['Voucher repeated in journal voucher.']})
        instance.refresh_from_db()
        JournalVoucher.apply_transactions(instance)
        return instance

    class Meta:
        model = JournalVoucher
        exclude = ('company',)


class JournalVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalVoucher
        fields = ('id', 'voucher_no', 'date', 'status', 'narration')


class JournalVoucherRowDetailSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name')

    class Meta:
        model = JournalVoucherRow
        fields = ('id', 'account_id', 'account_name', 'type', 'dr_amount', 'cr_amount')


class JournalVoucherDetailSerializer(serializers.ModelSerializer):
    rows = JournalVoucherRowDetailSerializer(many=True)

    class Meta:
        model = JournalVoucher
        fields = ('id', 'voucher_no', 'date', 'status', 'rows', 'narration')
