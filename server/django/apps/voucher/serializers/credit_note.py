from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError

from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin
from ..models import CreditNoteRow, CreditNote


class CreditNoteRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    discount = serializers.ReadOnlyField(source='discount_amount')

    class Meta:
        model = CreditNoteRow
        fields = ('item_id', 'tax_scheme_id', 'discount',)


class CreditNoteCreateSerializer(DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin, serializers.ModelSerializer):
    rows = CreditNoteRowSerializer(many=True)

    def assign_fiscal_year(self, validated_data, instance=None):
        if instance and instance.fiscal_year_id:
            return
        fiscal_year = self.context['request'].company.current_fiscal_year
        if fiscal_year.includes(validated_data.get('date')):
            validated_data['fiscal_year_id'] = fiscal_year.id
        else:
            raise ValidationError(
                {'date': ['Date not in current fiscal year.']},
            )

    def validate(self, data):
        if not data.get('party') and data.get('mode') == 'Credit' and data.get('status') != 'Draft':
            raise ValidationError(
                {'party': ['Party is required for a credit issue.']},
            )
        return data

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        credit_note = CreditNote.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            unit = row.pop('unit', None)
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            if unit:
                row['unit_id'] = unit.get('id')
            row = self.assign_discount_obj(row)
            CreditNoteRow.objects.create(voucher=credit_note, item_id=item.get('id'), **row)
        return credit_note

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        sale_vouchers = validated_data.pop('sale_vouchers')
        CreditNote.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            row['cash_receipt'] = instance
            try:
                CreditNoteRow.objects.update_or_create(pk=row.get('id'), defaults=row)
            except IntegrityError:
                raise APIException({'non_field_errors': ['Voucher repeated in cash receipt.']})
        instance.sale_vouchers.clear()
        instance.sale_vouchers.add(*sale_vouchers)
        instance.refresh_from_db()
        CreditNote.apply_transactions(instance)
        return instance

    class Meta:
        model = CreditNote
        exclude = ('company',)


class CreditNoteListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = CreditNote
        fields = ('id', 'voucher_no', 'party', 'date',)
