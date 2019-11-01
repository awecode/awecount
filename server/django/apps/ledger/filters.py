from django_filters import rest_framework as filters

from apps.ledger.models import Category


class AccountFilterSet(filters.FilterSet):
    pass


class CategoryFilterSet(filters.FilterSet):
    class Meta:
        model = Category
        fields = ('default',)
