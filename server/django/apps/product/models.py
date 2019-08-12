from django.db import models

from apps.ledger.models import Account, Category as AccountCategory
from apps.tax.models import TaxScheme
from apps.users.models import Company


class Unit(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


LEDGER_TYPES = (
    ('Use Global Ledger', 'Use Global Ledger'),
    ('Use Category\'s Ledger', 'Use Category\'s Ledger'),
    ('Use Dedicated Ledger', 'Use Dedicated Ledger'),
)


class Category(models.Model):
    name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    default_unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    default_tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, related_name='categories', on_delete=models.SET_NULL)

    sales_ledger = models.OneToOneField(Account, null=True, on_delete=models.SET_NULL, related_name='sales_category')
    purchase_ledger = models.OneToOneField(Account, null=True, on_delete=models.SET_NULL, related_name='purchase_category')
    discount_allowed_ledger = models.OneToOneField(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                   related_name='discount_allowed_category')
    discount_received_ledger = models.OneToOneField(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                    related_name='discount_received_category')
    
    items_sales_ledger_type = models.CharField(max_length=100, choices=LEDGER_TYPES)
    items_purchase_ledger_type = models.CharField(max_length=100, choices=LEDGER_TYPES)
    items_discount_allowed_ledger_type = models.CharField(max_length=100, choices=LEDGER_TYPES)
    items_discount_received_ledger_type = models.CharField(max_length=100, choices=LEDGER_TYPES)
    

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name='items')
    description = models.TextField(blank=True, null=True)
    selling_price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    sales_ledger = models.OneToOneField(Account, null=True, on_delete=models.SET_NULL, related_name='sales_item')
    purchase_ledger = models.OneToOneField(Account, null=True, on_delete=models.SET_NULL, related_name='purchase_item')
    discount_allowed_ledger = models.OneToOneField(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                   related_name='discount_allowed_item')
    discount_received_ledger = models.OneToOneField(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                                    related_name='discount_received_item')
    tax_scheme = models.ForeignKey(TaxScheme, blank=True, null=True, related_name='items', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    company = models.ForeignKey(Company, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.purchase_ledger:
            ledger = Account(name=self.name + ' (Purchase)', company=self.company)
            try:
                ledger.category = AccountCategory.objects.get(name='Purchase', parent__name='Expenses', company=self.company)
            except AccountCategory.DoesNotExist:
                pass
            ledger.code = 'P-' + str(self.code)
            ledger.save()
            self.purchase_ledger = ledger
        if not self.sales_ledger:
            ledger = Account(name=self.name + ' (Sales)', company=self.company)
            try:
                ledger.category = AccountCategory.objects.get(name='Sales', parent__name='Income', company=self.company)
            except AccountCategory.DoesNotExist:
                pass
            ledger.code = 'S-' + str(self.code)
            ledger.save()
            self.sales_ledger = ledger
        if not self.discount_allowed_ledger:
            discount_allowed_ledger = Account(name='Discount Allowed ' + self.name, company=self.company)
            discount_allowed_ledger.code = 'DA-' + str(self.code)
            try:
                discount_allowed_ledger.category = AccountCategory.objects.get(
                    name='Discount Expenses',
                    parent__name='Indirect Expenses',
                    company=self.company
                )
            except AccountCategory.DoesNotExist:
                pass
            discount_allowed_ledger.save()
            self.discount_allowed_ledger = discount_allowed_ledger
        if not self.discount_received_ledger:
            discount_received_ledger = Account(name='Discount Received ' + self.name, company=self.company)
            discount_received_ledger.code = 'DR-' + str(self.code)
            try:
                discount_received_ledger.category = AccountCategory.objects.get(
                    name='Discount Income',
                    parent__name='Indirect Income',
                    company=self.company
                )
            except AccountCategory.DoesNotExist:
                pass
            discount_received_ledger.save()
            self.discount_received_ledger = discount_received_ledger
        super(Item, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('code', 'company',)
