from django.apps import AppConfig, apps
from django.db.models import ManyToManyField
from django.db.models.signals import m2m_changed


class CompanyConfig(AppConfig):
    name = "apps.company"

    def ready(self) -> None:
        from django.core.cache import cache
        from apps.company.helpers import validate_company_in_m2m
        from apps.company.models import (
            CompanyBaseModel,
        )

        from .models import get_default_permissions

        global_permissions = get_default_permissions()
        cache.set("global_permissions", global_permissions)

        for model in apps.get_models():
            if not issubclass(model, CompanyBaseModel):
                continue

            fields = model._meta.get_fields()
            if not any(field.name == "company" for field in fields):
                continue

            for field in fields:
                if not isinstance(field, ManyToManyField):
                    continue

                related_model = field.related_model

                if not hasattr(related_model, "company"):
                    continue

                m2m_changed.connect(
                    validate_company_in_m2m,
                    sender=field.remote_field.through,
                    dispatch_uid=f"{model.__name__}_{field.name}_m2m_changed",
                )

        return super().ready()
