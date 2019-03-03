from django.db import models

from apps.ledger.models import Account, Category
from apps.users.models import Company


class Item(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    selling_price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    ledger = models.ForeignKey(Account, null=True, related_name='items', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(Company, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.ledger:
            ledger = Account(name=self.name)
            try:
                ledger.category = Category.objects.get(name='Purchase', parent__name='Expenses')
            except Category.DoesNotExist:
                pass
            ledger.code = 'P-' + str(self.id)
            ledger.save()
            self.ledger = ledger
        super(Item, self).save(*args, **kwargs)
