from django.db import models

from apps.company.models import Company


class SalesAgent(models.Model):
    name = models.CharField(max_length=255)
    compensation_multiplier = models.FloatField()
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sales_agents"
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "company")
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)
