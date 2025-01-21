from django.conf import settings
from django.db import models

from apps.company.models import Company, CompanyBaseModel
from apps.ledger.models import Account, JournalEntry, set_ledger_transactions


class TaxScheme(CompanyBaseModel):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rate = models.FloatField()
    recoverable = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="tax_schemes"
    )
    receivable = models.ForeignKey(
        Account,
        related_name="receivable_taxes",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    payable = models.ForeignKey(
        Account,
        related_name="payable_taxes",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.short_name or self.name

    @property
    def friendly_name(self):
        return self.short_name or self.name

    def save(self, *args, **kwargs):
        self.validate_unique()

        # needed for code generation
        super().save(*args, **kwargs)
        post_save = False

        acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES

        if self.recoverable and not self.receivable_id:
            receivable = Account(name=self.name + " Receivable", company=self.company)
            receivable.add_category(acc_cat_system_codes["Tax Receivables"])
            receivable.suggest_code(self)
            receivable.save()
            self.receivable = receivable
            post_save = True
        if not self.payable_id:
            payable = Account(name=self.name + " Payable", company=self.company)
            payable.add_category(acc_cat_system_codes["Duties & Taxes"])
            payable.suggest_code(self)
            payable.save()
            self.payable = payable
            post_save = True

        if post_save:
            self.save()

    @staticmethod
    def setup_nepali_tax_schemes(company):
        schemes = [
            TaxScheme(
                name="Value Added Tax",
                short_name="VAT",
                rate="13",
                recoverable=True,
                default=True,
                company=company,
            ),
            TaxScheme(
                name="Taxless",
                short_name="Taxless",
                rate="0",
                recoverable=False,
                default=True,
                company=company,
            ),
            TaxScheme(
                name="Export",
                short_name="Export",
                rate="0",
                recoverable=False,
                default=True,
                company=company,
            ),
            TaxScheme(
                name="Tax Deduction at Source",
                short_name="TDS",
                rate="1.5",
                recoverable=False,
                default=True,
                company=company,
            ),
            TaxScheme(
                name="TDS (Social Security Tax)",
                short_name="TDS-SST",
                rate="1",
                recoverable=False,
                default=True,
                company=company,
            ),
        ]
        # bulk doesn't work here because save isn't triggered and hence accounts are not created
        return [scheme.save() for scheme in schemes]

    class Meta:
        unique_together = ("short_name", "company")
        ordering = ["-id"]


STATUSES = (
    ("Draft", "Draft"),
    ("Paid", "Paid"),
    ("Cancelled", "Cancelled"),
)


class TaxPayment(CompanyBaseModel):
    voucher_no = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField()
    tax_scheme = models.ForeignKey(
        TaxScheme, related_name="payments", on_delete=models.CASCADE
    )
    amount = models.FloatField()
    remarks = models.TextField(blank=True, null=True)
    cr_account = models.ForeignKey(
        Account, related_name="tax_payments", on_delete=models.CASCADE
    )
    status = models.CharField(choices=STATUSES, max_length=10, default="Draft")

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="tax_payments"
    )

    def get_voucher_no(self):
        return self.voucher_no

    def get_source_id(self):
        return self.id

    def __str__(self):
        return self.voucher_no or self.date

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == "Paid":
            self.apply_transactions()
        if self.status == "Cancelled":
            self.cancel_transactions()

    def apply_transactions(self):
        entries = [
            ["dr", self.tax_scheme.payable, self.amount],
            ["cr", self.cr_account, self.amount],
        ]
        set_ledger_transactions(self, self.date, *entries, clear=True)

    def cancel_transactions(self):
        JournalEntry.objects.filter(
            content_type__model="taxpayment", object_id=self.id
        ).delete()

    def journal_entries(self):
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        qs = JournalEntry.objects.filter(content_type__app_label=app_label)
        qs = qs.filter(content_type__model=model, object_id=self.id)
        return qs
