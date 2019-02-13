from apps.ledger.serializers import PartySerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet


class PartyViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = PartySerializer
