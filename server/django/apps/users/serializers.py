from rest_framework import serializers

from apps.company.models import Company, FiscalYear
from apps.users.models import Role, User
from lib.drf.serializers import BaseModelSerializer


class CompanySerializer(BaseModelSerializer):
    request = None
    logo_url = serializers.SerializerMethodField()
    current_fiscal_year = serializers.ReadOnlyField(source="current_fiscal_year.name")
    current_fiscal_year_id = serializers.ReadOnlyField(source="current_fiscal_year.id")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def get_logo_url(self, obj):
        if not obj.logo:
            return
        if self.request:
            request = self.request
            return request.build_absolute_uri(obj.logo.url)
        elif self.context.get("request"):
            request = self.context.get("request")
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url

    class Meta:
        model = Company
        fields = "__all__"


class RoleSerializer(BaseModelSerializer):
    modules = serializers.ListField()

    class Meta:
        model = Role
        fields = ("id", "name", "modules")


class FiscalYearSerializer(BaseModelSerializer):
    # Maintain backward compatibility with the old field names
    start = serializers.DateField(source="start_date")
    end = serializers.DateField(source="end_date")

    class Meta:
        model = FiscalYear
        exclude = ()


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number"]
        read_only_fields = ["email"]


class UserLiteSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
        ]
