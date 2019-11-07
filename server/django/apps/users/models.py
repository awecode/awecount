import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.exceptions import APIException
from separatedvaluesfield.models import SeparatedValuesField

from apps.users.signals import company_creation
from .permission_modules import module_pairs

ORGANIZATION_TYPES = (
    ('private_limited', 'Private Limited'), ('public_limited', 'Public Limited'), ('sole_proprietorship', 'Sole Proprietorship'),
    ('partnership', 'Partnership'), ('corporation', 'Corporation'), ('non_profit', 'Non-profit'))


class FiscalYear(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return self.name

    def includes(self, date):
        return self.start <= date <= self.end


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True)
    contact_no = models.CharField(max_length=25)
    email = models.EmailField()
    organization_type = models.CharField(max_length=255, choices=ORGANIZATION_TYPES, default='private_limited')
    tax_registration_number = models.IntegerField()
    # force_preview_before_save = models.BooleanField(default=False)
    enable_sales_invoice_update = models.BooleanField(default=False)
    enable_cheque_deposit_update = models.BooleanField(default=False)
    enable_credit_note_update = models.BooleanField(default=False)
    enable_debit_note_update = models.BooleanField(default=False)
    enable_sales_agents = models.BooleanField(default=False)
    synchronize_cbms_nepal_test = models.BooleanField(default=False)
    synchronize_cbms_nepal_live = models.BooleanField(default=False)
    current_fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='companies')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Companies'

    def get_fiscal_years(self):
        # TODO Assign fiscal years to companies (m2m), return related fiscal years here
        return sorted(FiscalYear.objects.all(), key=lambda fy: 999 if fy.id == self.current_fiscal_year_id else fy.id,
                      reverse=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        super(Company, self).save(*args, **kwargs)
        if created:
            company_creation.send(sender=None, company=self)


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


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    modules = SeparatedValuesField(choices=module_pairs, max_length=3000, blank=True, null=True, token=',')

    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    roles = models.ManyToManyField(Role, blank=True, related_name='users')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name='users', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', ]

    objects = UserManager()

    @cached_property
    def role_modules(self):
        modules = []
        for role in self.roles.all():
            modules.extend(role.modules)
        return modules

    def __str__(self):
        return self.full_name

    def is_staff(self):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def check_perm(self, perm):
        if perm not in self.role_modules:
            raise APIException({'detail': 'User does not have enough permissions to perform the action.'})


class AccessKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4())
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_user(cls, key):
        try:
            return cls.objects.filter(enabled=True).select_related('user__company').get(key=key).user
        except (cls.DoesNotExist, ValidationError):
            return

    @classmethod
    def get_company(cls, key):
        try:
            return cls.objects.filter(enabled=True).select_related('user__company').get(key=key).user.company
        except (cls.DoesNotExist, ValidationError):
            return

    def __str__(self):
        return str(self.user)
