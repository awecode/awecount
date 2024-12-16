from rest_framework.permissions import SAFE_METHODS, BasePermission


class APIKeyPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous or getattr(request.user, "is_api", False):
            return False

        api_key = getattr(request.user, "api_key", None)

        if not api_key:
            return False

        if request.method in SAFE_METHODS and not request.method == "GET":
            return True

        model = view.model.__name__.lower()
        action = view.action

        return api_key.permissions.get(model, {}).get(action, False)
