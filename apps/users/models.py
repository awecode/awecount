from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.exceptions import APIException

from apps.company.models import Company
from awecounting.libs.fields import ChoiceArrayField

from .permission_modules import module_pairs


class UserManager(BaseUserManager):
    def create_user(self, email, full_name="", password=None, superuser=False):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=UserManager.normalize_email(email),
            full_name=full_name,
        )
        user.set_password(password)
        user.is_superuser = superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name="", password=None):
        return self.create_user(
            email, password=password, full_name=full_name, superuser=True
        )


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    modules = ChoiceArrayField(
        models.CharField(max_length=32, blank=True, choices=module_pairs),
        default=list,
        blank=True,
    )

    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    roles = models.ManyToManyField(Role, blank=True, related_name="users")
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, related_name="users", null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "full_name",
    ]

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
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def check_perm(self, perm):
        if perm not in self.role_modules:
            raise APIException(
                {
                    "detail": "User does not have enough permissions to perform the action."
                }
            )
