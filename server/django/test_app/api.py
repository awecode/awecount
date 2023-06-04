from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.bank import models, serializers

from . import data

class TestView(GenericViewSet):

    queryset = models.Account.objects.all()
    serializer_class = serializers.BankAccountSerializer
    permission_classes = [AllowAny]

    @action(['get'], detail=False, url_path='category-tree')
    def get_category_tree(self, request):
        return Response(data.category_tree)

    @action(['get'], detail=False, url_path='data')
    def get_data(self, request):
        return Response(data.data)