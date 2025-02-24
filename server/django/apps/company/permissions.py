# Third Party imports
from rest_framework.permissions import SAFE_METHODS, BasePermission

# Module imports
from apps.company.models import CompanyMember
from lib.string import to_snake


class CompanyBasePermission(BasePermission):
    """
    This permission class is used to check if the user has permission to access the company.
    Don't use this permission class directly. Use the following permission classes instead:
    - `CompanyOwnerPermission`
    - `CompanyAdminPermission`
    - `CompanyMemberPermission` (for member level permissions)
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        # allow anyone registered user to create a company
        if request.method == "POST":
            return True

        if request.method == "GET":
            return CompanyMember.objects.filter(
                member=request.user,
                company=request.company,
                is_active=True,
            ).exists()

        ## Safe Methods
        if request.method in SAFE_METHODS:
            return True

        # allow only admins and members to update the company settings
        if request.method in ["PUT", "PATCH"]:
            return CompanyMember.objects.filter(
                member=request.user,
                company=request.company,
                is_active=True,
                role__in=[
                    CompanyMember.Role.OWNER,
                    CompanyMember.Role.ADMIN,
                ],
            ).exists()

        # allow only owner to delete the company
        if request.method == "DELETE":
            return CompanyMember.objects.filter(
                member=request.user,
                company=request.company,
                is_active=True,
                role=CompanyMember.Role.OWNER,
            ).exists()


class CompanyOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        return CompanyMember.objects.filter(
            company=request.company,
            member=request.user,
            role=CompanyMember.Role.OWNER,
            is_active=True,
        ).exists()


class CompanyAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        return CompanyMember.objects.filter(
            member=request.user,
            company=request.company,
            role__in=[
                CompanyMember.Role.OWNER,
                CompanyMember.Role.ADMIN,
            ],
            is_active=True,
        ).exists()


class CompanyMemberPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        company_member = CompanyMember.objects.filter(
            member=request.user,
            company=request.company,
            is_active=True,
        ).first()

        if not company_member:
            return False

        if company_member.role in [
            CompanyMember.Role.OWNER,
            CompanyMember.Role.ADMIN,
        ]:
            return True

        if request.method in SAFE_METHODS and not request.method == "GET":
            return True

        DEFAULT_ACTION_MAPPING = {
            "create": "create",
            "list": "read",
            "retrieve": "read",
            "update": "update",
            "partial_update": "update",
            "destroy": "delete",
        }

        DEFAULT_METHOD_MAPPING = {
            "POST": "create",
            "GET": "read",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

        model = to_snake(view.model.__name__)
        action = None

        # Get the action from the view.action and if it is not present in the
        # DEFAULT_ACTION_MAPPING, then use the view.action itself.
        if hasattr(view, "action"):
            action = DEFAULT_ACTION_MAPPING.get(view.action, view.action)
        else:
            action = DEFAULT_METHOD_MAPPING.get(request.method)

        return company_member.permissions_dict.get(model, {}).get(action, False)
