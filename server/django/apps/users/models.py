from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone

ORGANIZATION_TYPES = (
    ('sole_proprietorship', 'Sole Proprietorship'), ('partnership', 'Partnership'), ('corporation', 'Corporation'),
    ('non_profit', 'Non-profit'))


class Company(models.Model):
    name = models.CharField(max_length=254)
    address = models.TextField()
    logo = models.ImageField(blank=True, null=True)
    contact_no = models.CharField(max_length=25, blank=True, null=True)
    organization_type = models.CharField(max_length=254, choices=ORGANIZATION_TYPES, default='sole_proprietorship')
    tax_registration_number = models.IntegerField(blank=True, null=True)


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=245)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', ]
