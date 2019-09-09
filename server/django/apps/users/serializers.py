from rest_framework import serializers

from apps.users.models import Company, User, Role, FiscalYear


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    modules = serializers.ListField()

    class Meta:
        model = Role
        fields = ('id', 'name', 'modules')


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.ReadOnlyField(source='role_modules')

    class Meta:
        model = User
        exclude = ('company', 'date_joined', 'password',)


class FiscalYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalYear
        exclude = ()
