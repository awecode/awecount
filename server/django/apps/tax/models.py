from django.db import models

from apps.users.models import Company


class TaxScheme(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rate = models.FloatField()
    recoverable = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tax_schemes')

    def __str__(self):
        return self.short_name or self.name
