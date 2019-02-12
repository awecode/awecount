from rest_framework import serializers

from apps.ledger.models import Party


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        exclude = ('company',)
