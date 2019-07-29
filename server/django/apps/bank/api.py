from apps.bank.models import BankAccount
from apps.bank.serializers import BankAccountSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class BankAccountViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
