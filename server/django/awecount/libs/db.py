from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.db.models import Sum

from apps.company.models import Company


class DistinctSum(Sum):
    function = "SUM"
    template = "%(function)s(DISTINCT %(expressions)s)"


def validate_company_in_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "pre_add":
        instance_company = getattr(instance, "company")
        if instance_company is None:
            raise SuspiciousOperation(
                instance.__class__.__name__ + " does not reference any company."
            )
        related_instances = model.objects.filter(pk__in=pk_set)
        for related_instance in related_instances:
            related_instance_company = getattr(related_instance, "company", None)
            if related_instance_company is None:
                raise SuspiciousOperation(
                    related_instance.__class__.__name__
                    + " does not reference any company."
                )
            if related_instance_company != instance_company:
                raise SuspiciousOperation(
                    related_instance.__class__.__name__
                    + " references a different company."
                )


class CompanyBaseModel(models.Model):
    class Meta:
        abstract = True

    def check_company_references(self, instance):
        """
        Check that all ForeignKey relationships that reference a `Company`
        have the instance's `company` if it exists or all related instances have the same `company`.
        """
        instance_company = getattr(instance, "company", None)

        for field in instance._meta.get_fields():
            if not isinstance(field, models.ForeignKey):
                continue

            related_model = field.related_model
            if related_model == Company:
                continue
            related_instance = getattr(instance, field.name, None)

            if not related_instance or hasattr(related_instance, "company") is False:
                continue

            if related_instance.company is None:
                raise SuspiciousOperation(
                    field.name + " does not reference any company."
                )

            if instance_company is None:
                instance_company = related_instance.company
            elif related_instance.company != instance_company:
                raise SuspiciousOperation(
                    field.name + " references a different company."
                )

    def save(self, *args, **kwargs):
        self.check_company_references(self)
        super().save(*args, **kwargs)
