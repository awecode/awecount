from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.product.models import Item
from apps.product.serializers.partner import PartnerItemSerializer


class PartnerItemViewSet(ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = PartnerItemSerializer
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(
            company_id=self.request.company_id,
            account__isnull=False,
            code__isnull=False,
        ).prefetch_related("account")
