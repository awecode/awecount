from rest_framework.decorators import action

from apps.ledger.models.base import Account
from apps.ledger.serializers import AccountSerializer
from apps.voucher.serializers.payment_mode import (
    PaymentModeCreateSerializer,
    PaymentModeListSerializer,
    PaymentModeRetrieveSerializer,
)
from awecount.libs.CustomViewSet import CRULViewSet
from awecount.libs.mixins import InputChoiceMixin


class PaymentModeViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = PaymentModeListSerializer
    collections = (
        (
            "accounts",
            Account,
            AccountSerializer,
            True,
            ["code", "name"],
        ),
    )

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return PaymentModeCreateSerializer
        if self.action == "retrieve":
            return PaymentModeRetrieveSerializer
        return super().get_serializer_class()

    @action(detail=False)
    def choices(self, request):
        res = super().choices(request)
        if res.data["pagination"]["page"] == 1:
            res.data["results"].insert(
                0,
                {
                    "id": "credit",
                    "name": "Credit",
                },
            )
        return res
