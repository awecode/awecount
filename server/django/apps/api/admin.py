from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from apps.api.models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "prefix",
        "name",
        "created_at",
        "expiry_date",
        "has_expired",
        "revoked",
    )
    list_filter = ("created_at", "company", "revoked")
    search_fields = ("company__name", "name", "prefix")

    def get_readonly_fields(self, request, obj=None):
        fields = ("prefix",)
        if obj is not None and obj.revoked:
            fields = fields + ("name", "revoked", "expiry_date")

        return fields

    def save_model(
        self,
        request,
        obj: APIKey,
        form=None,
        change=False,
    ):
        created = not obj.pk

        if created:
            key = self.model.objects.assign_key(obj)
            obj.save()
            message = _(
                "The API key for {} is: {}. ".format(obj.name, key)
                + "Please store it somewhere safe: "
                + "you will not be able to see it again."
            )
            messages.add_message(request, messages.WARNING, message)
        else:
            obj.save()
