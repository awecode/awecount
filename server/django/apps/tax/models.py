from django.db import models

from apps.ledger.models import Account
from apps.users.models import Company


class TaxScheme(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=5, blank=True, null=True)
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
