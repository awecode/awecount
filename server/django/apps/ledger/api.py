from apps.ledger.serializers import PartySerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class PartyViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = PartySerializer
