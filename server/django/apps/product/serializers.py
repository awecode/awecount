from django.core.files.base import ContentFile
from rest_framework import serializers

from awecount.utils.Base64FileField import Base64FileField
from .models import Item, Unit, Category as InventoryCategory
from .validators import CustomUniqueTogetherValidator


class ItemSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    unit_id = serializers.IntegerField(required=False)
    front_image = Base64FileField(required=False, allow_null=True)
    back_image = Base64FileField(required=False, allow_null=True)

    @staticmethod
    def base64_check(validated_data, attributes):
        for attr in attributes:
            if validated_data.get(attr) and not isinstance(validated_data.get(attr),
                                                                            ContentFile):
                validated_data.pop(attr)
        return validated_data

    def create(self, validated_data):
        # validated_data = self.base64_check(validated_data, ['front_image', 'back_image'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.base64_check(validated_data, ['front_image', 'back_image'])
        return super().update(instance, validated_data)


    class Meta:
        model = Item
        exclude = ('company', 'tax_scheme', 'unit',)
        validators = [
            CustomUniqueTogetherValidator(
                queryset=Item.objects.all(),
                fields=('code', 'company_id',),
                message="Item with code exists."
            )
        ]


class UnitSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()

    class Meta:
        model = Unit
        exclude = ('company',)


class InventoryCategorySerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField()
    default_unit_id = serializers.IntegerField(required=False)
    default_tax_scheme_id = serializers.IntegerField(required=False)

    class Meta:
        model = InventoryCategory
        exclude = ('company', 'default_unit', 'default_tax_scheme')
