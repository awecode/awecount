from django.db.models import Sum


class DistinctSum(Sum):
    function = "SUM"
    template = "%(function)s(DISTINCT %(expressions)s)"
