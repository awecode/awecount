from rest_framework import serializers

from apps.ledger.models import set_transactions as set_ledger_transactions, Account
from .models import SalesVoucherRow, SalesVoucher


class SalesVoucherRowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(source='item.id', required=True)
    tax_scheme_id = serializers.IntegerField(source='tax_scheme.id', required=True)
    voucher_id = serializers.IntegerField(source='voucher.id', required=False, read_only=True)

    class Meta:
        model = SalesVoucherRow
        exclude = ('item', 'tax_scheme', 'voucher')


class SalesVoucherCreateSerializer(serializers.ModelSerializer):
    rows = SalesVoucherRowSerializer(many=True)
    company_id = serializers.IntegerField()

    def apply_transactions(self, voucher):
        entries = []
        discount_expense = Account.objects.get(name='Discount Expenses', company=voucher.company,
                                               category__name='Indirect Expenses')

        # TODO Voucher discount needs to broken into row discounts
        # if voucher.discount and voucher.discount_expense:
        #     set_ledger_transactions(voucher, voucher.transaction_date, ['dr', discount_expense, voucher.discount_amount])

        # dr_acc = voucher.party.customer_account
        for row in voucher.rows.all():
            tax_amt = 0
            total = row.quantity * row.rate

            # TODO If the voucher has discount, apply discount proportionally
            # if discount_rate:
            #     if obj.tax == 'inclusive' and tax_scheme:
            #         discount_rate = discount_rate * 100 / (100 + tax_scheme.percent)
            #     divident_discount = (pure_total - row_discount) * discount_rate

            entries.append(['cr', row.item.ledger, total])

            if row.tax_scheme:
                tax_amt = (total) * row.tax_scheme.rate / 100
                entries.append(['cr', row.tax_scheme.payable, tax_amt])

            if row.discount and row.discount_expense:
                entries.append(['dr', discount_expense, row.discount_amount])

            # TODO receivalble account create in party
            receivable = total - row.discount_amount + tax_amt
            # entries.append(['dr', dr_acc, receivable])

            set_ledger_transactions(row, voucher.transaction_date, *entries)
        return

    def create(self, validated_data):
        rows_data = validated_data.pop('rows')
        request = self.context['request']
        user_id = request.user.id
        validated_data['user_id'] = user_id
        voucher = SalesVoucher.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            SalesVoucherRow.objects.create(voucher=voucher, item_id=item.get('id'), **row)
        return voucher

    def update(self, instance, validated_data):
        rows_data = validated_data.pop('rows')
        SalesVoucher.objects.filter(pk=instance.id).update(**validated_data)
        for index, row in enumerate(rows_data):
            item = row.pop('item')
            row['voucher'] = instance
            row['item_id'] = item.get('id')
            tax_scheme = row.pop('tax_scheme')
            row['tax_scheme_id'] = tax_scheme.get('id')
            SalesVoucherRow.objects.update_or_create(pk=row.get('id'), defaults=row)
        instance.refresh_from_db()
        return instance

    class Meta:
        model = SalesVoucher
        exclude = ('company', 'user',)


class SalesVoucherListSerializer(serializers.ModelSerializer):
    party = serializers.ReadOnlyField(source='party.name')

    class Meta:
        model = SalesVoucher
        fields = ('id', 'voucher_no', 'party', 'transaction_date', 'status',)
