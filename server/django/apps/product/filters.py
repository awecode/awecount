from django_filters import rest_framework as filters

from .models import Item, InventoryAccount


class ItemFilterSet(filters.FilterSet):
    class Meta:
        model = Item
        fields = ('can_be_sold', 'can_be_purchased')
