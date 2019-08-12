from rest_framework import serializers

from apps.users.models import Company, User, Role


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
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ('company', 'date_joined', 'password',)
