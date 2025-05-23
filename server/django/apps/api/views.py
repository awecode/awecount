from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from apps.api.models import APIKey
from apps.api.serializers import APIKeySerializer
from apps.company.permissions import CompanyAdminPermission


class APIKeyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, CompanyAdminPermission]

    def get_queryset(self):
        return APIKey.objects.filter(
            user=self.request.user,
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        api_key, key = APIKey.objects.create_key(
            name=serializer.validated_data['name'],
            user=request.user,
            expiry_date=serializer.validated_data.get('expiry_date'),
        )

        data = serializer.data
        data['key'] = key

        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.revoked = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
