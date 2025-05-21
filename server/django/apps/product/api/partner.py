from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.product.models import Item
from apps.product.serializers.partner import PartnerItemListSerializer
from django.db.models import Sum, F, Value as V, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce


class PartnerItemViewSet(ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = PartnerItemListSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset.filter(
            company_id=self.request.company.id,
            account__isnull=False,
            code__isnull=False,
        ).prefetch_related("account")

        queryset = queryset.annotate(
            dr_amount=Coalesce(
                Sum("account__transactions__dr_amount"),
                V(0),
                output_field=DecimalField(),
            ),
            cr_amount=Coalesce(
                Sum("account__transactions__cr_amount"),
                V(0),
                output_field=DecimalField(),
            ),
        ).annotate(
            current_balance=ExpressionWrapper(
                F("dr_amount") - F("cr_amount"), output_field=DecimalField()
            )
        )
        return queryset
