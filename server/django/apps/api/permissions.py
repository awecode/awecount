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

        DEFAULT_ACTION_MAPPING = {
            "create": "create",
            "list": "view",
            "retrieve": "view",
            "update": "modify",
            "partial_update": "modify",
            "destroy": "delete",
        }

        DEFAULT_METHOD_MAPPING = {
            "POST": "create",
            "GET": "view",
            "PUT": "modify",
            "PATCH": "modify",
            "DELETE": "delete",
        }

        model = view.model.__name__.lower()
        action = None

        # Get the action from the view.action and if it is not present in the
        # DEFAULT_ACTION_MAPPING, then use the view.action itself.
        if hasattr(view, "action"):
            action = DEFAULT_ACTION_MAPPING.get(view.action, view.action)
        else:
            action = DEFAULT_METHOD_MAPPING.get(request.method)

        return api_key.permissions.get(model, {}).get(action, False)
