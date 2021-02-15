from django.core.exceptions import SuspiciousOperation


class BadOperation(SuspiciousOperation):
    pass