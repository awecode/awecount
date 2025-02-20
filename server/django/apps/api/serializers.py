from rest_framework.serializers import ModelSerializer

from apps.api.models import APIKey


class APIKeySerializer(ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'prefix', 'created_at', 'expiry_date', 'revoked']
        read_only_fields = ['id', 'prefix', 'created_at']
