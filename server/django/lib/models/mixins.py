from crum import get_current_user
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TimeAuditModel(models.Model):
    """To path when the record was created and last modified"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Modified At",
    )

    class Meta:
        abstract = True


class UserAuditModel(models.Model):
    """To path when the record was created and last modified"""

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
        null=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated_by",
        verbose_name="Last Modified By",
        null=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user is None or user.is_anonymous:
            self.created_by = None
            self.updated_by = None
            super(UserAuditModel, self).save(*args, **kwargs)
        else:
            # Check if the model is being created or updated
            if self._state.adding:
                # If created only set created_by value: set updated_by to None
                self.created_by = user
                self.updated_by = None
            # If updated only set updated_by value don't touch created_by
            self.updated_by = user
            super(UserAuditModel, self).save(*args, **kwargs)


class AuditModel(TimeAuditModel, UserAuditModel):
    """To path when the record was created and last modified"""

    class Meta:
        abstract = True
