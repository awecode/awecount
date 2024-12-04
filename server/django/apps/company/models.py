import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from lib.constants import RESTRICTED_COMPANY_SLUGS
from lib.models import BaseModel


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


def slug_validator(value):
    if value in RESTRICTED_COMPANY_SLUGS:
        raise ValidationError("Slug is not valid")


TEMPLATE_CHOICES = [
    (1, "Template 1"),
    (2, "Template 2"),
    (3, "Template 3"),
    # (4, "Template 4")
]


def get_company_logo_path(instance, filename):
    _, ext = filename.split(".")
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"{instance.slug}/logo/{filename}"


class Company(BaseModel):
    class Type(models.TextChoices):
        PRIVATE_LIMITED = "private_limited", "Private Limited"
        PUBLIC_LIMITED = "public_limited", "Public Limited"
        SOLE_PROPRIETORSHIP = "sole_proprietorship", "Sole Proprietorship"
        PARTNERSHIP = "partnership", "Partnership"
        CORPORATION = "corporation", "Corporation"
        NON_PROFIT = "non_profit", "Non-profit"

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    name = models.CharField(max_length=255, verbose_name="Company Name")
    logo = models.ImageField(
        verbose_name="Logo",
        blank=True,
        null=True,
        # upload_to=get_company_logo_path,
        upload_to="logos/",
    )
    slug = models.SlugField(
        max_length=48,
        db_index=True,
        unique=True,
        validators=[
            slug_validator,
        ],
    )

    # legal information
    organization_type = models.CharField(
        max_length=255,
        choices=Type.choices,
        default=Type.PRIVATE_LIMITED,
    )
    tax_registration_number = models.CharField(max_length=255)

    # contact information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    country_iso = models.CharField(max_length=2, blank=True, null=True)
    postal_code = models.CharField(max_length=6, blank=True, null=True)
    phone = models.CharField(max_length=18, blank=True, null=True)
    alternate_phone = models.CharField(max_length=18, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    alternate_email = models.EmailField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)

    current_fiscal_year = models.ForeignKey(
        FiscalYear, on_delete=models.CASCADE, related_name="companies"
    )

    # config
    enable_sales_invoice_update = models.BooleanField(default=False)
    enable_cheque_deposit_update = models.BooleanField(default=False)
    enable_credit_note_update = models.BooleanField(default=False)
    enable_debit_note_update = models.BooleanField(default=False)
    enable_sales_agents = models.BooleanField(default=False)
    synchronize_cbms_nepal_test = models.BooleanField(default=False)
    synchronize_cbms_nepal_live = models.BooleanField(default=False)
    config_template = models.CharField(max_length=255, default="np")
    invoice_template = models.IntegerField(choices=TEMPLATE_CHOICES, default=1)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ("-id",)

    def __str__(self):
        """Return name of the Company"""
        return self.name

    def get_fiscal_years(self):
        # TODO Assign fiscal years to companies (m2m), return related fiscal years here
        return sorted(
            FiscalYear.objects.all(),
            key=lambda fy: 999 if fy.id == self.current_fiscal_year_id else fy.id,
            reverse=True,
        )
