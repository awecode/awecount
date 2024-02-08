from django.db import models

from apps.users.models import Company


class InvoiceDesign(models.Model):
    design = models.ImageField(upload_to="design/")
    canvas = models.TextField()
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="invoice"
    )

    def __str__(self):
        return self.company.name + " " + "Invoice"
