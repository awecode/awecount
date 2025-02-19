from rest_framework import serializers

from apps.company.constants import RESTRICTED_COMPANY_SLUGS
from apps.company.models import Company, CompanyMember, CompanyMemberInvite
from apps.users.serializers import UserLiteSerializer


class CompanyLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "slug", "logo", "id"]
        read_only_fields = fields


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "name",
            "organization_type",
            "tax_registration_number",
            "country",
            "country_iso",
            "currency_code",
            "slug",
        ]
        read_only_fields = ["slug"]


class CompanySerializer(serializers.ModelSerializer):
    owner = UserLiteSerializer(read_only=True)
    total_members = serializers.IntegerField(read_only=True)
    logo_url = serializers.CharField(read_only=True)
    current_fiscal_year = serializers.CharField(source="current_fiscal_year.name", read_only=True)
    current_fiscal_year_id = serializers.IntegerField(read_only=True)


    def validate_slug(self, value):
        # Check if the slug is restricted
        if value in RESTRICTED_COMPANY_SLUGS:
            raise serializers.ValidationError("Slug is not valid")
        return value

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "owner",
            "logo_url",
        ]


class CompanyMemberSerializer(serializers.ModelSerializer):
    member = UserLiteSerializer(read_only=True)
    company = CompanyLiteSerializer(read_only=True)

    class Meta:
        model = CompanyMember
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "company",
            "member",
        ]


class CompanyMemberInviteSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    total_members = serializers.IntegerField(read_only=True)
    created_by_detail = UserLiteSerializer(read_only=True, source="created_by")

    class Meta:
        model = CompanyMemberInvite
        fields = "__all__"
        read_only_fields = [
            "id",
            "email",
            "token",
            "company",
            "message",
            "responded_at",
            "created_at",
            "updated_at",
        ]
