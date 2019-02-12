from rest_framework import viewsets

from apps.ledger.models import Party
from apps.ledger.serializers import PartySerializer


class PartyViewSet(viewsets.ModelViewSet):
    serializer_class = PartySerializer

    def get_queryset(self):
        company = self.request.company
        return Party.objects.filter(company=company)
