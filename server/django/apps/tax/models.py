from django.db import models

from apps.ledger.models import Account
from apps.users.models import Company


class TaxScheme(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rate = models.FloatField()
    recoverable = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tax_schemes')
    receivable = models.ForeignKey(Account, related_name='tax_receivable', blank=True, null=True,
                                   on_delete=models.CASCADE)
    payable = models.ForeignKey(Account, related_name='tax_payable', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.short_name or self.name

    def save(self, *args, **kwargs):
        if self.pk is None:
            receivable = Account(name=self.name + ' Receivable')
            receivable.company = self.company
            receivable.suggest_code()
            receivable.save()
            self.receivable = receivable
            payable = Account(name=self.name + ' Payable')
            payable.company = self.company
            payable.add_category('Duties & Taxes')
            payable.suggest_code()
            payable.save()
            self.payable = payable
        self.receivable.category = None
        if self.recoverable:
            self.receivable.add_category('Tax Receivables')
            self.receivable.suggest_code()
        self.receivable.save()
        super(TaxScheme, self).save(*args, **kwargs)

    @staticmethod
    def setup_nepali_tax_schemes(company):
        schemes = [
            TaxScheme(name='Value Added Tax', short_name='VAT', rate='13', recoverable=True, default=True, company=company),
            TaxScheme(name='Taxless', short_name='Taxless', rate='0', recoverable=False, default=True, company=company),
            TaxScheme(name='Export', short_name='Export', rate='0', recoverable=False, default=True, company=company),
            TaxScheme(name='Tax Deduction at Source', short_name='TDS', rate='1.5', recoverable=False, default=True,
                      company=company),
        ]
        return TaxScheme.objects.bulk_create((schemes))

    class Meta:
        unique_together = ('short_name', 'company')


STATUSES = (
    ('Draft', 'Draft'),
    ('Paid', 'Paid'),
    ('Cancelled', 'Cancelled'),
)


class TaxPayment(models.Model):
    voucher_no = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField()
    tax_scheme = models.ForeignKey(TaxScheme, related_name='payments', on_delete=models.CASCADE)
    amount = models.FloatField()
    remarks = models.TextField(blank=True, null=True)
    cr_account = models.ForeignKey(Account, related_name='tax_payments', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUSES, max_length=10, default='Draft')

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tax_payments')

    def __str__(self):
        return self.voucher_no or self.date

        # def apply_transactions(self):


