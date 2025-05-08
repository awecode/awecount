from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils import timezone
from apps.ledger.serializers import PartyMinSerializer
from apps.product.models import Item
from awecount.libs import get_next_quotation_no
from awecount.libs.CustomViewSet import GenericSerializer
from awecount.libs.serializers import StatusReversionMixin
from lib.drf.serializers import BaseModelSerializer
from apps.product.serializers import ItemSalesSerializer
from apps.quotation.models import Quotation, QuotationRow, QuotationSetting
from apps.voucher.serializers.mixins import (
    DiscountObjectTypeSerializerMixin,
)
from apps.tax.serializers import TaxSchemeSerializer
from apps.voucher.serializers.sales import (
    SalesAgentSerializer,
    SalesDiscountSerializer,
    SalesVoucherRowDetailSerializer,
)


class QuotationChoiceSerializer(BaseModelSerializer):
    class Meta:
        model = Quotation
        fields = ("id", "number", "date", "status", "customer_name", "total_amount")


class QuotationListSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")

    class Meta:
        model = Quotation
        fields = (
            "id",
            "number",
            "party_name",
            "date",
            "status",
            "customer_name",
            "total_amount",
        )


class QuotationRowSerializer(DiscountObjectTypeSerializerMixin, BaseModelSerializer):
    id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=True)
    tax_scheme_id = serializers.IntegerField(required=False, allow_null=True)
    unit_id = serializers.IntegerField(required=False)
    item_name = serializers.ReadOnlyField(source="item.name")
    amount_before_tax = serializers.ReadOnlyField()
    amount_before_discount = serializers.ReadOnlyField()
    hs_code = serializers.ReadOnlyField(source="item.category.hs_code")
    selected_item_obj = ItemSalesSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")

    def validate_discount(self, value):
        if not value:
            value = 0
        elif value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value

    class Meta:
        model = QuotationRow
        exclude = ("item", "tax_scheme", "quotation", "unit", "discount_obj")
        extra_kwargs = {
            "discount": {"allow_null": True, "required": False},
            "discount_type": {"allow_null": True, "required": False},
        }


class QuotationCreateSerializer(
    StatusReversionMixin,
    DiscountObjectTypeSerializerMixin,
    BaseModelSerializer,
):
    number = serializers.ReadOnlyField()
    rows = QuotationRowSerializer(many=True)
    quotation_meta = serializers.ReadOnlyField()

    selected_party_obj = PartyMinSerializer(source="party", read_only=True)
    selected_sales_agent_obj = GenericSerializer(source="sales_agent", read_only=True)

    def assign_quotation_number(self, validated_data, instance):
        if instance and instance.number:
            return
        if validated_data.get("status") == "Draft":
            return
        next_quotation_no = get_next_quotation_no(
            Quotation, self.context["request"].company.id
        )
        validated_data["number"] = next_quotation_no

    def validate(self, data):
        if data.get("discount") and data.get("discount") < 0:
            raise ValidationError({"discount": ["Discount cannot be negative."]})

        return data

    def validate_rows(self, rows):
        item_ids = [row.get("item_id") for row in rows]
        items = {item.id: item for item in Item.objects.filter(id__in=item_ids)}

        for row in rows:
            item_id = row.get("item_id")
            item = items.get(item_id)
            if not item:
                raise serializers.ValidationError({"item_id": ["Item not found."]})

            row_serializer = QuotationRowSerializer(
                data=row, context={"request": self.context["request"]}
            )
            if not row_serializer.is_valid():
                raise serializers.ValidationError(row_serializer.errors)
        return rows

    def create(self, validated_data):
        rows_data = validated_data.pop("rows")
        request = self.context["request"]
        self.assign_quotation_number(validated_data, instance=None)
        self.assign_discount_obj(validated_data)
        validated_data["company_id"] = request.company.id
        validated_data["user_id"] = request.user.id
        instance = Quotation.objects.create(**validated_data)
        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            if row.get("id"):
                row.pop("id")
            QuotationRow.objects.create(quotation=instance, **row)
        quotation_meta = instance.get_quotation_meta(update_row_data=True)
        instance.total_amount = quotation_meta["grand_total"]
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data["status"] == "Generated":
            if instance.status == "Draft":
                validated_data["generated_datetime"] = timezone.now()
        rows_data = validated_data.pop("rows")
        self.validate_voucher_status(validated_data, instance)
        self.assign_quotation_number(validated_data, instance)
        self.assign_discount_obj(validated_data)
        validated_data["company_id"] = self.context["request"].company.id
        Quotation.objects.filter(pk=instance.id).update(**validated_data)

        for index, row in enumerate(rows_data):
            row = self.assign_discount_obj(row)
            QuotationRow.objects.update_or_create(
                quotation=instance, pk=row.get("id"), defaults=row
            )

        instance.refresh_from_db()
        quotation_meta = instance.get_quotation_meta(update_row_data=True)
        instance.total_amount = quotation_meta["grand_total"]
        instance.save()
        if instance.total_amount != quotation_meta["grand_total"]:
            instance.total_amount = quotation_meta["grand_total"]
            instance.save()
        return instance

    class Meta:
        model = Quotation
        exclude = (
            "company",
            "user",
            "discount_obj",
        )


class QuotationRowDetailSerializer(BaseModelSerializer):
    item_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    tax_scheme_id = serializers.IntegerField()
    item_name = serializers.ReadOnlyField(source="item.name")
    unit_name = serializers.ReadOnlyField(source="unit.name")
    discount_obj = SalesDiscountSerializer()
    tax_scheme = TaxSchemeSerializer()
    hs_code = serializers.ReadOnlyField(source="item.category.hs_code")
    selected_item_obj = ItemSalesSerializer(read_only=True, source="item")
    selected_unit_obj = GenericSerializer(read_only=True, source="unit")

    class Meta:
        model = QuotationRow
        exclude = ("number", "item", "unit")


class QuotationDetailSerializer(BaseModelSerializer):
    party_name = serializers.ReadOnlyField(source="party.name")
    party_contact_no = serializers.ReadOnlyField(source="party.contact_no")
    party_email = serializers.ReadOnlyField(source="party.email")
    discount_obj = SalesDiscountSerializer()
    quotation_meta = serializers.ReadOnlyField(source="get_quotation_meta")
    sales_agent = SalesAgentSerializer()

    rows = SalesVoucherRowDetailSerializer(many=True)
    tax_identification_number = serializers.ReadOnlyField(
        source="party.tax_identification_number"
    )
    footer_text = serializers.ReadOnlyField(source="company.quotation_settings.footer_text")
    body_text = serializers.ReadOnlyField(source="company.quotation_settings.body_text")
    # TODO: quotation footer texts

    class Meta:
        model = Quotation
        exclude = (
            "company",
            "user",
        )


class QuotationCreateSettingSerializer(BaseModelSerializer):
    class Meta:
        model = QuotationSetting
        fields = ("fields", "options")


class QuotationSettingCreateSerializer(BaseModelSerializer):
    class Meta:
        model = QuotationSetting
        exclude = ("company",)


class QuotationSettingUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = QuotationSetting
        fields = ("options",)


class QuotationSettingsSerializer(BaseModelSerializer):
    class Meta:
        model = QuotationSetting
        exclude = ("company",)
