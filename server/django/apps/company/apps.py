from django.apps import AppConfig


class CompanyConfig(AppConfig):
    name = "apps.company"

    def ready(self) -> None:
        from django.core.cache import cache

        from .models import get_default_permissions

        global_permissions = get_default_permissions()
        cache.set("global_permissions", global_permissions)

        return super().ready()
