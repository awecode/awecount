import random
import string
import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import APIException

from apps.company.models import Company
from awecount.libs.fields import ChoiceArrayField
from lib.models.mixins import TimeAuditModel


def get_default_onboarding():
    return {
        "profile_complete": False,
        "company_create": False,
        "company_invite": False,
        "company_join": False,
    }


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
        models.CharField(max_length=32, blank=True),
        default=list,
        blank=True,
    )

    def __str__(self):
        return self.name


def get_avatar_upload_path(instance, filename):
    _, ext = filename.split(".")
    filename = f"{uuid.uuid4()}.{ext}"
    return f"avatars/{filename}"


class User(AbstractBaseUser):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )
    email = models.CharField(max_length=255, unique=True)

    # user fields
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to=get_avatar_upload_path, blank=True, null=True)

    # tracking metrics
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_location = models.CharField(max_length=255, blank=True)
    created_location = models.CharField(max_length=255, blank=True)

    # the is' es
    is_superuser = models.BooleanField(default=False)
    is_password_expired = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_password_autoset = models.BooleanField(default=False)

    # the last's
    last_active = models.DateTimeField(default=timezone.now, null=True)
    last_login_time = models.DateTimeField(null=True)
    last_logout_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(max_length=20, default="email")
    last_login_uagent = models.TextField(blank=True)

    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    @property
    def company(self):
        return Company.objects.filter(company_members__member=self).first()

    @property
    def company_id(self):
        return self.company.id if self.company else None

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()

        if not self.full_name:
            self.full_name = (
                self.email.split("@")[0]
                if len(self.email.split("@"))
                else "".join(random.choice(string.ascii_letters) for _ in range(6))
            )

        super(User, self).save(*args, **kwargs)

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


class Profile(TimeAuditModel):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        primary_key=True,
    )

    # User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=300, null=True, blank=True)  # job role

    # Onboarding
    is_onboarded = models.BooleanField(default=False)
    onboarding_step = models.JSONField(default=get_default_onboarding)
    is_tour_completed = models.BooleanField(default=False)

    # Last visited company
    last_company_id = models.UUIDField(null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ("-created_at",)
