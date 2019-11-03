from django_filters import rest_framework as filters

from .models import Item


class ItemFilterSet(filters.FilterSet):
    class Meta:
        model = Item
        fields = ('can_be_sold', 'can_be_purchased', 'search_data',)


class BookFilterSet(filters.FilterSet):
    language = filters.CharFilter(field_name="extra_data__language")
    genre = filters.CharFilter(field_name="extra_data__genre")
    format = filters.CharFilter(field_name="extra_data__format")

    class Meta:
        model = Item
        fields = ('can_be_sold', 'can_be_purchased', 'search_data', 'brand',)
