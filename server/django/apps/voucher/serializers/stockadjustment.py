from rest_framework import serializers
from awecount.libs.serializers import StatusReversionMixin

from apps.voucher.models import StockAdjustmentVoucher
from awecount.libs import get_next_voucher_no


class StockAdjustmentVoucherCreateSerializer(StatusReversionMixin,serializers.ModelSerializer):
    voucher_no=serializers.ReadOnlyField()
    

    def assign_voucher_number(self, validated_data, instance):
            
            if instance and instance.voucher_no:
                return
            if validated_data.get('status') in ['Cancelled']:
                return
            next_voucher_no = get_next_voucher_no(StockAdjustmentVoucher, self.context['request'].company_id)
            validated_data['voucher_no'] = next_voucher_no

    def create(self,validated_data):
        self.assign_voucher_number(validated_data, instance=None)
        instance = StockAdjustmentVoucher.objects.create(**validated_data)
        return instance
    
    class Meta:
        model = StockAdjustmentVoucher
        fields =['id','voucher_no','date','status']

class StockAdjustmentVoucherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustmentVoucher
        fields = ['id','voucher_no', 'date','status']

class StockAdjustmentVoucherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustmentVoucher
        fields = ['id','voucher_no', 'date','status']