from rest_framework import viewsets

from apps.ledger.models import Party
from apps.ledger.serializers import PartySerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet


class PartyViewSet(CreateListRetrieveUpdateViewSet):
    serializer_class = PartySerializer

    def get_queryset(self):
        company = self.request.company
        return Party.objects.filter(company=company)
