from rest_framework import serializers

from apps.users.models import Company, User, Role, FiscalYear


class CompanySerializer(serializers.ModelSerializer):
    request = None
    logo_url = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def get_logo_url(self, obj):
        if not obj.logo:
            return
        if self.request:
            request = self.request
            return request.build_absolute_uri(obj.logo.url)
        elif self.context.get('request'):
            request = self.context.get('request')
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url

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
