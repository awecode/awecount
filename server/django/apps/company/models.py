import uuid
import warnings
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from lib.constants import RESTRICTED_COMPANY_SLUGS
from lib.models import BaseModel


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

    @property
    def current_fiscal_year(self):
        return self.company_fiscalyears.filter(is_current=True).first()

    @property
    def current_fiscal_year_id(self):
        return self.current_fiscal_year.id

    def get_fiscal_years(self):
        return self.company_fiscalyears.all()


class CompanyBaseModel(BaseModel):
    company = models.ForeignKey(
        Company,
        models.CASCADE,
        related_name="company_%(class)s",
    )

    class Meta:
        abstract = True


class FiscalYear(CompanyBaseModel):
    name = models.CharField(max_length=24)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(
        default=False,
        help_text=_(
            "Indicates if this is the currently selected fiscal year for the company"
        ),
    )

    class Meta:
        unique_together = ["company", "start_date", "end_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "is_current"],
                condition=Q(is_current=True),
                name="unique_current_fiscal_year_per_company",
            ),
        ]
        verbose_name = "Company Fiscal Year"
        verbose_name_plural = "Company Fiscal Years"
        ordering = ("-start_date", "is_current")

    def __str__(self):
        return self.name

    @property
    def previous_day(self):
        return self.start_date - timedelta(days=1)

    def contains_date(self, date):
        return self.start_date <= date <= self.end_date

    def includes(self, date):
        warnings.warn(
            "FiscalYear.includes() is deprecated, use FiscalYear.contains_date() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.contains_date(date)

    def clean(self):
        super().clean()
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(
                    {"end_date": _("End date must be after start date.")}
                )

            overlapping = (
                FiscalYear.objects.filter(company=self.company)
                .exclude(pk=self.pk)
                .filter(
                    Q(start_date__lte=self.end_date) & Q(end_date__gte=self.start_date)
                )
                .exists()
            )

            if overlapping:
                raise ValidationError(
                    _(
                        "This fiscal year overlaps with an existing fiscal year for this company."
                    )
                )

    def save(self, *args, **kwargs):
        if self.is_current:
            (
                FiscalYear.objects.filter(company=self.company, is_current=True)
                .exclude(pk=self.pk)
                .update(is_current=False)
            )
        self.full_clean()
        super().save(*args, **kwargs)
