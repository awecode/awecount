from rest_framework import serializers

# Serializer mixins need to inherit from serializers.Serializer
class DiscountObjectTypeSerializerMixin(serializers.Serializer):
    discount_type = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, obj):
        fields = super().to_representation(obj)
        if obj.discount_obj_id:
            fields['discount_type'] = obj.discount_obj_id
        return fields

    def assign_discount_obj(self, validated_data):
        discount_key = validated_data.get('discount_type')
        if discount_key and str(discount_key).isdigit():
            validated_data['discount_obj_id'] = discount_key
            validated_data['discount'] = 0
            validated_data['discount_type'] = None
        else:
            validated_data['discount_obj_id'] = None
        return validated_data
    
class ModeCumBankSerializerMixin(serializers.Serializer):
    mode = serializers.CharField(required=True)
    bank_account_id = serializers.IntegerField(required=False, allow_null=True)

    def assign_mode(self, validated_data):
        mode = validated_data.get('mode')
        if mode and str(mode).isdigit():
            validated_data['bank_account_id'] = mode
            validated_data['mode'] = 'Bank Deposit'
        else:
            validated_data['bank_account_id'] = None
        return validated_data

    def to_representation(self, obj):
        if obj.mode == 'Bank Deposit' and obj.bank_account_id:
            self.fields['mode'] = serializers.IntegerField(source='bank_account_id')
        return super().to_representation(obj)