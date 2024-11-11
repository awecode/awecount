from apps.ledger.models.base import Account
from apps.ledger.serializers import AccountSerializer
from apps.voucher.serializers.payment_mode import (
    PaymentModeCreateSerializer,
    PaymentModeListSerializer,
    PaymentModeRetrieveSerializer,
)
from awecount.libs.CustomViewSet import CRULViewSet


class PaymentModeViewSet(CRULViewSet):
    serializer_class = PaymentModeCreateSerializer
    collections = (
        (
            "accounts",
            Account,
            AccountSerializer,
            True,
            ["code", "name"],
        ),
        # (
        #     "transaction_fee_account",
        #     Account,
        #     AccountListSerializer,
        #     True,
        #     ["code", "name"],
        # ),
    )

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentModeListSerializer
        if self.action == "retrieve":
            return PaymentModeRetrieveSerializer
        return super().get_serializer_class()
