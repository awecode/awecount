from django.db import models

from apps.company.models import Company

DISCOUNT_TYPES = (
    ("Amount", "Amount"),
    ("Percent", "Percent"),
)


class Discount(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=25, choices=DISCOUNT_TYPES)
    value = models.FloatField()
    trade_discount = models.BooleanField(default=True)

    def __str__(self):
        if self.name:
            return self.name
        return "{} - {}".format(self.type, self.value)

    class Meta:
        abstract = True
        ordering = ["-id"]


class SalesDiscount(Discount):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sales_discounts"
    )


class PurchaseDiscount(Discount):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="purchase_discounts"
    )
