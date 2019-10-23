from django_filters import rest_framework as filters

from .models import Item


class ItemFilterSet(filters.FilterSet):

    class Meta:
        model = Item
        fields = ('can_be_sold', 'can_be_purchased', 'search_data',)
