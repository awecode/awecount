from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Account
from .serializers import PartySerializer, AccountSerializer, AccountDetailSerializer
from awecount.utils.CustomViewSet import CreateListRetrieveUpdateViewSet
from awecount.utils.mixins import InputChoiceMixin


class PartyViewSet(InputChoiceMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = PartySerializer


class AccountViewSet(InputChoiceMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccountDetailSerializer
        return AccountSerializer

    @action(detail=True, methods=['get'])
    def project_fy_cr_ledger_choices(self, request, pk=None):
        instance = self.get_object()
        data = AccountSerializer(instance, many=True).data
        return Response(data)
