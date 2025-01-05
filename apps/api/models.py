import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.users.models import User


class AccessKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4)
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_user(cls, key):
        try:
            return (
                cls.objects.filter(enabled=True)
                .select_related("user__company")
                .get(key=key)
                .user
            )
        except (cls.DoesNotExist, ValidationError):
            return

    @classmethod
    def get_company(cls, key):
        try:
            return (
                cls.objects.filter(enabled=True)
                .select_related("user__company")
                .get(key=key)
                .user.company
            )
        except (cls.DoesNotExist, ValidationError):
            return

    def __str__(self):
        return str(self.user)
