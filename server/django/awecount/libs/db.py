from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.db.models import Sum

from apps.company.models import Company


class DistinctSum(Sum):
    function = "SUM"
    template = "%(function)s(DISTINCT %(expressions)s)"


class CompanyBaseModel(models.Model):
    class Meta:
        abstract = True

    def check_company_references(self, instance):
        """
        Check that all ForeignKey and ManyToManyField relationships that reference a `Company`
        have the instance's `company` if it exists or all related instances have the same `company`.
        """
        instance_company = getattr(instance, "company", None)

        for field in instance._meta.get_fields():
            related_instances = []
            if not isinstance(field, (models.ForeignKey, models.ManyToManyField)):
                continue

            if isinstance(field, models.ForeignKey):
                related_model = field.related_model
                if related_model == Company:
                    continue
                related_instance = getattr(instance, field.name, None)
                if related_instance:
                    related_instances = [related_instance]

            elif instance.pk is not None:
                related_model = field.related_model
                if related_model == Company:
                    continue
                related_instances = getattr(instance, field.name).all()

            for related_instance in related_instances:
                if not hasattr(related_instance, "company"):
                    continue
                if instance_company is None:
                    instance_company = related_instance.company
                elif related_instance.company != instance_company:
                    raise SuspiciousOperation("Company mismatch.")

    def save(self, *args, **kwargs):
        self.check_company_references(self)
        super().save(*args, **kwargs)
