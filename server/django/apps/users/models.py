from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
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


class UserManager(BaseUserManager):
    def create_user(self, email, full_name='', password=None, superuser=False):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=UserManager.normalize_email(email),
            full_name=full_name,
        )
        user.set_password(password)
        user.is_superuser = superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name='', password=None):
        return self.create_user(
            email,
            password=password,
            full_name=full_name,
            superuser=True
        )


class User(PermissionsMixin, AbstractBaseUser):
    full_name = models.CharField(max_length=245)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', ]

    objects = UserManager()

    def is_staff(self):
        return self.is_superuser
