from django.db import models

from apps.users.models import Company


class Item(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    selling_price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    
    company = models.ForeignKey(Company, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
