from django.db import models

from apps.users.models import Company


class Party(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True)
    contact_no = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    tax_registration_number = models.IntegerField(blank=True, null=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='parties')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Parties'
