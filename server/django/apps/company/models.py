from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import SuspiciousOperation
from django.db import models

ORGANIZATION_TYPES = (
    ("private_limited", "Private Limited"),
    ("public_limited", "Public Limited"),
    ("sole_proprietorship", "Sole Proprietorship"),
    ("partnership", "Partnership"),
    ("corporation", "Corporation"),
    ("non_profit", "Non-profit"),
)


class FiscalYear(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return self.name

    def includes(self, date):
        return self.start <= date <= self.end

    @property
    def previous_day(self):
        return self.start - timedelta(days=1)


class Company(models.Model):
    TEMPLATE_CHOICES = [
        (1, "Template 1"),
        (2, "Template 2"),
        (3, "Template 3"),
        # (4, "Template 4")
    ]

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True, upload_to="logos/")
    contact_no = models.CharField(max_length=25)
    # email = models.EmailField()
    emails = ArrayField(models.EmailField(), default=list, blank=True)
    website = models.URLField(blank=True, null=True)
    organization_type = models.CharField(
        max_length=255, choices=ORGANIZATION_TYPES, default="private_limited"
    )
    tax_registration_number = models.IntegerField()
    # force_preview_before_save = models.BooleanField(default=False)
    enable_sales_invoice_update = models.BooleanField(default=False)
    enable_cheque_deposit_update = models.BooleanField(default=False)
    enable_credit_note_update = models.BooleanField(default=False)
    enable_debit_note_update = models.BooleanField(default=False)
    enable_sales_agents = models.BooleanField(default=False)
    synchronize_cbms_nepal_test = models.BooleanField(default=False)
    synchronize_cbms_nepal_live = models.BooleanField(default=False)
    current_fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="companies"
    )
    config_template = models.CharField(max_length=255, default="np")
    invoice_template = models.IntegerField(choices=TEMPLATE_CHOICES, default=1)
    currency_code = models.CharField(max_length=10, default="NPR")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"

    def get_fiscal_years(self):
        # TODO Assign fiscal years to companies (m2m), return related fiscal years here
        return sorted(
            FiscalYear.objects.all(),
            key=lambda fy: 999 if fy.id == self.current_fiscal_year_id else fy.id,
            reverse=True,
        )

    def save(self, *args, **kwargs):
        created = not self.pk
        super(Company, self).save(*args, **kwargs)
        # if created:
        #     company_creation.send(sender=None, company=self)


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
