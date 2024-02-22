from rest_framework import serializers

from apps.voucher.models import StockAdjustmentVoucher
from awecount.libs import get_next_voucher_no


class StockAdjustmentVoucherCreateSerializer(serializers.ModelSerializer):
    voucher_no=serializers.ReadOnlyField()
    

    def assign_voucher_number(self, validated_data, instance):
            
            if instance and instance.voucher_no:
                return
            if validated_data.get('status') in ['Cancelled']:
                return
            next_voucher_no = get_next_voucher_no(StockAdjustmentVoucher, self.context['request'].company_id)
            validated_data['voucher_no'] = next_voucher_no

    class Meta:
        model = StockAdjustmentVoucher
        fields =['voucher_no','date']

class StockAdjustmentVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustmentVoucher
        fields = ['voucher_no', 'date']

class StockAdjustmentVoucherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustmentVoucher
        fields = ['voucher_no', 'date']