from django.dispatch import Signal

company_creation = Signal(providing_args=["company"])
