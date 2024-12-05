from django.apps import AppConfig


class CompanyConfig(AppConfig):
    name = "apps.company"

    def ready(self) -> None:
        from django.core.cache import cache

        from .models import get_default_permissions

        # The ultimate purpose of this is to scan and check syntax of all permission metas.
        # Later on maybe, we can utilize the cached data.

        global_permissions = get_default_permissions()
        cache.set("global_permissions", global_permissions)

        return super().ready()
