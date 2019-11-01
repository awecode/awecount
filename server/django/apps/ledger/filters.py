from django.db.models import Q
from django_filters import rest_framework as filters

from apps.ledger.models import Category, Account


class HasBalanceFilter(filters.BooleanFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(Q(current_dr__isnull=False) | Q(current_cr__isnull=False))
        return qs


class CategoryFilter(filters.ModelChoiceFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(category__in=value.get_descendants(include_self=True))
        return qs


class AccountFilterSet(filters.FilterSet):
    has_balance = HasBalanceFilter()
    category = CategoryFilter(queryset=Category.objects.all())

    class Meta:
        model = Account
        fields = ('default',)


class CategoryFilterSet(filters.FilterSet):
    class Meta:
        model = Category
        fields = ('default',)
