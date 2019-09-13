from django.db import models


class SalesAgent(models.Model):
    name = models.CharField(max_length=255)
    compensation_multiplier = models.FloatField(default=1)

    def __str__(self):
        return self.name
