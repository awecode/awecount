# Third Party imports
from rest_framework.permissions import SAFE_METHODS, BasePermission

# Module imports
from apps.company.models import CompanyMember


class CompanyBasePermission(BasePermission):
    """
    This permission class is used to check if the user has permission to access the company.
    Don't use this permission class directly. Use the following permission classes instead:
    - `CompanyOwnerPermission`
    - `CompanyAdminPermission`
    - `CompanyEntityPermission` (for member level permissions)
    - `CompanyGuestPermission`
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        company_slug = view.kwargs.get("company_slug", None)

        if not company_slug:
            return False

        # allow anyone registered user to create a company
        if request.method == "POST":
            return True

        if request.method == "GET":
            return CompanyMember.objects.filter(
                member=request.user,
                company__slug=company_slug,
                is_active=True,
            ).exists()

        ## Safe Methods
        if request.method in SAFE_METHODS:
            return True

        # allow only admins and members to update the company settings
        if request.method in ["PUT", "PATCH"]:
            return CompanyMember.objects.filter(
                member=request.user,
                company__slug=company_slug,
                is_active=True,
                access_level__in=[
                    CompanyMember.AccessLevel.OWNER,
                    CompanyMember.AccessLevel.ADMIN,
                ],
            ).exists()

        # allow only owner to delete the company
        if request.method == "DELETE":
            return CompanyMember.objects.filter(
                member=request.user,
                company__slug=company_slug,
                is_active=True,
                access_level=CompanyMember.AccessLevel.OWNER,
            ).exists()


class CompanyOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        company_slug = view.kwargs.get("company_slug", None)

        if not company_slug:
            return False

        return CompanyMember.objects.filter(
            company__slug=company_slug,
            member=request.user,
            access_level=CompanyMember.AccessLevel.OWNER,
            is_active=True,
        ).exists()


class CompanyAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        company_slug = view.kwargs.get("company_slug", None)

        if not company_slug:
            return False

        return CompanyMember.objects.filter(
            member=request.user,
            company__slug=company_slug,
            access_level__in=[
                CompanyMember.AccessLevel.OWNER,
                CompanyMember.AccessLevel.ADMIN,
            ],
            is_active=True,
        ).exists()


class CompanyMemberPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        company_slug = view.kwargs.get("company_slug", None)

        if not company_slug:
            return False

        company_member = CompanyMember.objects.filter(
            member=request.user,
            company__slug=company_slug,
            is_active=True,
        ).first()

        if not company_member:
            return False

        if company_member.access_level in [
            CompanyMember.AccessLevel.OWNER,
            CompanyMember.AccessLevel.ADMIN,
        ]:
            return True

        if request.method in SAFE_METHODS and not request.method == "GET":
            return True

        model = view.model.__name__.lower()
        action = view.action

        return company_member.permissions_dict.get(model, {}).get(action, False)
