from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models

from apps.company.models import Company, CompanyBaseModel
from apps.ledger.models import Account, JournalEntry
from apps.ledger.models import set_transactions as set_ledger_transactions
from awecount.libs import get_next_voucher_no


class JournalVoucher(models.Model):
    STATUSES = [
        ("Cancelled", "Cancelled"),
        ("Approved", "Approved"),
        ("Unapproved", "Unapproved"),
    ]

    voucher_no = models.IntegerField()
    date = models.DateField()
    narration = models.TextField()
    status = models.CharField(max_length=10, choices=STATUSES, default="Unapproved")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("company", "voucher_no")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.pk and not self.voucher_no:
            self.voucher_no = get_next_voucher_no(JournalVoucher, self.company_id)

    def get_source_id(self):
        return self.id

    def get_total_dr_amount(self):
        total_dr_amount = 0
        for o in self.rows.all():
            total_dr_amount += o.dr_amount
        return total_dr_amount

    def get_total_cr_amount(self):
        total_cr_amount = 0
        for o in self.rows.all():
            total_cr_amount += o.cr_amount
        return total_cr_amount

    def get_voucher_no(self):
        return self.voucher_no

    def apply_transactions(self):
        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if not self.status == "Approved":
            return

        entries = []
        # filter bypasses rows cached by prefetching
        for row in self.rows.filter().select_related("account"):
            amount = row.dr_amount if row.type == "Dr" else row.cr_amount
            entries.append([row.type.lower(), row.account, amount])
        # set_ledger_transactions needs to be outside the for loop for a balanced entry (Dr/Cr match)
        set_ledger_transactions(self, self.date, *entries, clear=True)
        return

    def cancel(self, reason=""):
        self.status = "Cancelled"
        self.cancel_transactions()
        if reason:
            self.narration = (
                "{}\nReason for cancellation: {}".format(self.narration, reason)
                if self.narration
                else reason
            )
        self.save()

    def cancel_transactions(self):
        content_type = ContentType.objects.get(model="journalvoucher")
        # row_ids = self.rows.values_list('id', flat=True)
        # JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()
        JournalEntry.objects.filter(
            content_type=content_type, object_id=self.id
        ).delete()

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)


class JournalVoucherRow(CompanyBaseModel):
    TYPES = [("Dr", "Dr"), ("Cr", "Cr")]
    type = models.CharField(choices=TYPES, default="Dr", max_length=2)
    account = models.ForeignKey(
        Account, related_name="journal_voucher_rows", on_delete=models.CASCADE
    )
    description = models.TextField(null=True, blank=True)
    dr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    cr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    journal_voucher = models.ForeignKey(
        JournalVoucher,
        related_name="rows",
        on_delete=models.CASCADE,
    )

    company_id_accessor = "journal_voucher__company_id"

    def get_source_id(self):
        return self.journal_voucher_id

    def get_voucher_no(self):
        return self.journal_voucher.voucher_no
