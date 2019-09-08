from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from awecount.utils import get_next_voucher_no
from awecount.utils.serializers import StatusReversionMixin
from .mixins import DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin
from ..models import DebitNoteRow, DebitNote


class DebitNoteRowSerializer(DiscountObjectTypeSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=True)
    unit_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = DebitNoteRow
        exclude = ('item', 'tax_scheme', 'voucher', 'unit', 'discount_obj')


class DebitNoteCreateSerializer(StatusReversionMixin, DiscountObjectTypeSerializerMixin, ModeCumBankSerializerMixin,
                                 serializers.ModelSerializer):
    voucher_no = serializers.ReadOnlyField()
    rows = DebitNoteRowSerializer(many=True)

    def assign_voucher_number(self, validated_data, instance):
        if instance and instance.voucher_no:
            return
        if validated_data.get('status') in ['Draft', 'Cancelled']:
            return
        next_voucher_no = get_next_voucher_no(DebitNote, self.context['request'].company_id)
        validated_data['voucher_no'] = next_voucher_no

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
        invoices = validated_data.pop('invoices')
        request = self.context['request']
        self.assign_fiscal_year(validated_data, instance=None)
        self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        validated_data['company_id'] = request.company_id
        validated_data['user_id'] = request.user.id
        instance = DebitNote.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            DebitNoteRow.objects.create(voucher=instance, **row)
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        return instance

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        invoices = validated_data.pop('invoices')
        self.validate_voucher_status(validated_data, instance)
        self.assign_voucher_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        self.assign_mode(validated_data)
        DebitNote.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            DebitNoteRow.objects.update_or_create(voucher=instance, pk=row.get('id'), defaults=row)
        instance.invoices.clear()
        instance.invoices.add(*invoices)
        instance.refresh_from_db()
        DebitNote.apply_transactions(instance)
        return instance

    class Meta:
        model = DebitNote
        exclude = ('company', 'user', 'bank_account', 'discount_obj', 'fiscal_year',)


class DebitNoteListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = DebitNote
        fields = ('id', 'voucher_no', 'party', 'date',)
