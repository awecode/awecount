from django.core.exceptions import SuspiciousOperation


def validate_company_in_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "pre_add":
        instance_company = getattr(instance, "company")
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
