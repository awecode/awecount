from django.apps import AppConfig
from django.db.models import ManyToManyField
from django.db.models.signals import m2m_changed


class VoucherConfig(AppConfig):
    name = "apps.voucher"

    def ready(self) -> None:
        from apps.company.models import Company
        from awecount.libs.db import CompanyBaseModel, validate_company_in_m2m

        for model in self.get_models():
            if not issubclass(model, CompanyBaseModel):
                continue

            fields = model._meta.get_fields()
            if not any(field.name == "company" for field in fields):
                continue

            for field in fields:
                if not isinstance(field, ManyToManyField):
                    continue

                related_model = field.related_model
                if related_model == Company:
                    continue

                if not hasattr(related_model, "company"):
                    continue

                m2m_changed.connect(
                    validate_company_in_m2m,
                    sender=field.remote_field.through,
                    dispatch_uid=f"{model.__name__}_{field.name}_m2m_changed",
                )
