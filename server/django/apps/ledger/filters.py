from functools import reduce
from django.db.models import Q
from apps.ledger.models.base import Transaction
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


class IexactInFilter(filters.BaseCSVFilter):
    def filter(self, qs, value):
        if value:
            q_list = map(lambda n: Q(
                **{self.field_name + '__iexact': n}), value)
            q_list = reduce(lambda a, b: a | b, q_list)
            qs = qs.filter(q_list)
        return qs
    
class NumberFilter(filters.Filter):
    def filter(self, qs, value):
        if value:
            return qs.filter(**{f"{self.field_name}__exact": value})
        return qs


class TransactionFilterSet(filters.FilterSet):
    account = NumberFilter(field_name='account_id')
    source = NumberFilter(field_name='journal_entry__content_type_id')
    category = NumberFilter(field_name='account__category_id')

    class Meta:
        model = Transaction
        fields = []
