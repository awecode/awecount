from django.db import models

from apps.ledger.models import Account, Category
from apps.tax.models import TaxScheme
from apps.users.models import Company


class Item(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    selling_price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    ledger = models.ForeignKey(Account, null=True, related_name='items', on_delete=models.SET_NULL)
    discount_allowed_ledger = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL, related_name='allowed_items')
    discount_payable_ledger = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL, related_name='payable_items')
    tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, related_name='items', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(Company, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.ledger:
            ledger = Account(name=self.name, company=self.company)
            try:
                ledger.category = Category.objects.get(name='Purchase', parent__name='Expenses', company=self.company)
            except Category.DoesNotExist:
                pass
            ledger.code = 'P-' + str(self.code)
            ledger.save()
            self.ledger = ledger
        if not self.discount_allowed_ledger:
            discount_allowed_ledger = Account(name='Discount Allowed ' + self.name, company=self.company)
            discount_allowed_ledger.code = 'D-' + str(self.code)
            try:
                discount_allowed_ledger.category = Category.objects.get(
                    name='Discount Expenses',
                    parent__name='Indirect Expenses',
                    company=self.company
                )
            except Category.DoesNotExist:
                pass
                discount_allowed_ledger.save()
            self.discount_allowed_ledger = discount_allowed_ledger
        if not self.discount_payable_ledger:
            discount_payable_ledger = Account(name='Discount Payable ' + self.name, company=self.company)
            discount_payable_ledger.code = 'D-' + str(self.code)
            # TODO confirm category
            # try:
            #     discount_ledger.category = Category.objects.get(
            #         name='Discount Expenses',
            #         parent__name='Indirect Expenses',
            #         company=self.company
            #     )
            # except Category.DoesNotExist:
            #     pass
            discount_payable_ledger.save()
            self.discount_payable_ledger = discount_payable_ledger
        super(Item, self).save(*args, **kwargs)
