from django.db import models

from apps.users.models import Company


class SalesAgent(models.Model):
    name = models.CharField(max_length=255)
    compensation_multiplier = models.FloatField(default=1)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales_agents')

    def __str__(self):
        return self.name
