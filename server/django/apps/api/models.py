import typing
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from lib.models.mixins import TimeAuditModel

from .crypto import KeyGenerator


class APIKeyManager(models.Manager):
    key_generator = KeyGenerator()

    def assign_key(self, obj: "APIKey") -> str:
        key, prefix, hashed_key = self.key_generator.generate()

        obj.id = uuid.uuid4()
        obj.prefix = prefix
        obj.hashed_key = hashed_key

        return key

    def create_key(self, **kwargs: typing.Any) -> typing.Tuple["APIKey", str]:
        # Prevent from manually setting the primary key.
        kwargs.pop("id", None)
        obj = self.model(**kwargs)
        key = self.assign_key(obj)
        obj.save()
        return obj, key

    def get_usable_keys(self) -> models.QuerySet:
        return self.filter(revoked=False)

    def get_from_key(self, key: str) -> "APIKey":
        prefix, _, _ = key.partition(".")
        queryset = self.get_usable_keys()

        try:
            api_key = queryset.get(prefix=prefix)
        except self.model.DoesNotExist:
            raise  # For the sake of being explicit.

        if not api_key.is_valid(key):
            raise self.model.DoesNotExist("Key is not valid.")
        else:
            return api_key

    def validate_key(self, key: str) -> tuple["APIKey", bool]:
        try:
            api_key = self.get_from_key(key)
        except self.model.DoesNotExist:
            return None, False

        if api_key.has_expired:
            return api_key, False

        return api_key, True


class APIKey(TimeAuditModel):
    objects = APIKeyManager()

    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE )

    id = models.UUIDField(primary_key=True, editable=False)
    prefix = models.CharField(max_length=8, unique=True, editable=False)
    hashed_key = models.CharField(max_length=150, editable=False)

    name = models.CharField(
        max_length=50,
        blank=False,
        default="",
        help_text=(
            _(
                "A free-form name for the API key. "
                "Need not be unique. "
                "50 characters max."
            )
        ),
    )
    revoked = models.BooleanField(
        blank=True,
        default=False,
        help_text=(
            _(
                "If the API key is revoked, clients cannot use it anymore. "
                "(This cannot be undone.)"
            )
        ),
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Expires"),
        help_text=_("Once API key expires, clients cannot use it anymore."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")

    @property
    def has_expired(self):
        return self.expiry_date and self.expiry_date < timezone.now().date()

    def __str__(self):
        return str(self.name)

    def is_valid(self, key: str) -> bool:
        key_generator = self.objects.key_generator
        return key_generator.verify(key, self.hashed_key)
