import json

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django_q.tasks import async_task
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.company.models import (
    Company,
    CompanyMember,
    CompanyMemberInvite,
    FiscalYear,
    Permission,
    get_default_permissions,
)
from apps.company.permissions import (
    CompanyAdminPermission,
    CompanyBasePermission,
    CompanyMemberPermission,
)
from apps.company.serializers import (
    CompanyCreateSerializer,
    CompanyLiteSerializer,
    CompanyMemberInviteSerializer,
    CompanyMemberSerializer,
    CompanyPermissionSerializer,
    CompanySerializer,
)
from awecount.libs.nepdate import ad2bs, bs, bs2ad


class CompanyViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    model = Company
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, CompanyBasePermission]

    lookup_field = "slug"
    lookup_url_kwarg = "company_slug"

    def get_queryset(self):
        return self.model.objects.filter(slug=self.kwargs.get("company_slug"))

    def get_serializer_class(self):
        if self.action == "create":
            return CompanyCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Create the company member
        CompanyMember.objects.create(
            company=serializer.instance,
            member=request.user,
            role=CompanyMember.Role.OWNER,
        )

        country_iso = serializer.instance.country_iso
        current_year = timezone.now().year

        fiscal_year_details = self._get_fiscal_year_details(country_iso, current_year)

        fiscal_year, _ = FiscalYear.objects.get_or_create(
            start_date=fiscal_year_details["start_date"],
            end_date=fiscal_year_details["end_date"],
            name=fiscal_year_details["label"],
        )

        serializer.instance.current_fiscal_year = fiscal_year
        serializer.instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def _get_fiscal_year_details(self, country_iso, current_year):
        """Returns fiscal year details based on country ISO."""
        if country_iso == "NP":
            return self._get_nepal_fiscal_year_details()

        fiscal_year_map = {
            "IN": {
                "start_date": f"{current_year}-04-01",
                "end_date": f"{current_year + 1}-03-31",
                "label": f"FY {current_year}-{(current_year + 1) % 100}",  # 2021-22
            },
            "US": {
                "start_date": f"{current_year}-01-01",
                "end_date": f"{current_year}-12-31",
                "label": f"FY{current_year % 100}",  # FY21
            },
        }
        return fiscal_year_map.get(country_iso, {})

    def _get_nepal_fiscal_year_details(self):
        """Returns the fiscal year start/end dates for Nepal (BS to AD conversion)."""
        date = timezone.now().date()
        bs_date = ad2bs(date.strftime("%Y-%m-%d"))

        start = bs2ad(f"{bs_date[0]}-04-01")
        end = bs2ad(f"{bs_date[0] + 1}-03-{bs[bs_date[0] + 1][2]}")

        return {
            "start_date": f"{start[0]}-{start[1]:02d}-{start[2]:02d}",
            "end_date": f"{end[0]}-{end[1]:02d}-{end[2]:02d}",
            "label": f"{bs_date[0] % 100}/{(bs_date[0] + 1) % 100}",  # 78/79
        }

    @action(
        detail=True,
        methods=["post"],
        url_path="upload-logo",
    )
    def upload_logo(self, request, *args, **kwargs):
        """Upload company logo."""
        company = self.get_object()

        if "logo" not in request.FILES:
            return Response(
                {"error": "No logo file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        company.logo = request.FILES["logo"]
        company.save()

        return Response(CompanySerializer(company).data, status=status.HTTP_200_OK)


class CompanyPermissionViewSet(viewsets.ModelViewSet):
    model = Permission
    serializer_class = CompanyPermissionSerializer

    permission_classes = [permissions.IsAuthenticated, CompanyAdminPermission]

    def get_queryset(self):
        return self.model.objects.filter(company__slug=self.kwargs.get("company_slug"))

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def perform_update(self, serializer):
        serializer.save(company=self.request.company)

    @action(detail=False, methods=["get"])
    def defaults(self, request, *args, **kwargs):
        return Response(get_default_permissions(), status=status.HTTP_200_OK)


class CompanyMemberPermissionEndpoint(views.APIView):
    model = Permission
    permission_classes = [permissions.IsAuthenticated, CompanyMemberPermission]

    def get(self, request, company_slug):
        company_member = CompanyMember.objects.filter(
            company__slug=company_slug,
            member=request.user,
            is_active=True,
        ).first()

        if company_member is None:
            return Response(
                {"error": "You do not have permission to access this company"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "role": company_member.role,
                "permissions": company_member.permissions_dict,
            },
            status=status.HTTP_200_OK,
        )


class CompanyMemberViewSet(viewsets.ModelViewSet):
    model = CompanyMember
    serializer_class = CompanyMemberSerializer

    permission_classes = [permissions.IsAuthenticated, CompanyAdminPermission]

    def get_queryset(self):
        return self.filter_queryset(
            self.model.objects.filter(company=self.request.company)
            .select_related("company", "member")
            .filter(is_active=True)
        )

    def destroy(self, request, company_slug, pk):
        company_member = self.get_object()
        company_member.is_active = False
        company_member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyInvitationViewset(viewsets.ModelViewSet):
    model = CompanyMemberInvite
    serializer_class = CompanyMemberInviteSerializer

    permission_classes = [permissions.IsAuthenticated, CompanyAdminPermission]

    def get_queryset(self):
        return self.model.objects.filter(
            company__slug=self.kwargs.get("company_slug")
        ).select_related("company", "created_by")

    def _validate_emails(self, emails):
        """Validate email format and required fields."""
        if not emails:
            raise ValidationError("Emails are required")

        for email_data in emails:
            if not email_data.get("email"):
                raise ValidationError("Email is required")
            validate_email(email_data.get("email"))

            if email_data.get("role", "member") not in ["member", "admin"]:
                raise ValidationError("Invalid role")

    def _validate_permissions(self, requesting_user, emails):
        """Validate user permissions for inviting members."""
        role_permissions = {
            "member": [],
            "admin": ["member"],
            "owner": ["member", "admin"],
        }

        allowed_roles = role_permissions.get(requesting_user.role, [])
        if not allowed_roles:
            raise ValidationError("Members cannot invite anyone")

        for email_data in emails:
            role = email_data.get("role", "member")
            if role not in allowed_roles:
                raise ValidationError(
                    f"{requesting_user.role.title()}s can only invite {' and '.join(allowed_roles)}"
                )

    def _check_existing_members(self, company_id, emails):
        """Check if any invited users are already company members."""
        existing_members = CompanyMember.objects.filter(
            company_id=company_id,
            member__email__in=[email.get("email") for email in emails],
            is_active=True,
        ).select_related("member", "company", "company__owner")

        if existing_members.exists():
            return CompanyMemberSerializer(existing_members, many=True).data
        return None

    def _create_invitations(self, emails, company_id):
        """Create invitation objects for each email."""
        invitations = []
        default_permission = Permission.objects.get(
            company_id=company_id, name="Default"
        )
        for email_data in emails:
            email = email_data.get("email").strip().lower()

            invitations.append(
                CompanyMemberInvite(
                    email=email,
                    company_id=company_id,
                    role=email_data.get("role", "member"),
                    created_by=self.request.user,
                )
            )

        invitations = CompanyMemberInvite.objects.bulk_create(
            invitations, batch_size=10, ignore_conflicts=True
        )

        for invitation in invitations:
            invitation.permissions.set([default_permission])

        return invitations

    def create(self, request, company_slug):
        try:
            emails = request.data.get("emails", [])
            self._validate_emails(emails)

            requesting_user = CompanyMember.objects.get(
                company__slug=company_slug, member=request.user, is_active=True
            )

            self._validate_permissions(requesting_user, emails)

            company = Company.objects.get(slug=company_slug)
            existing_members = self._check_existing_members(company.id, emails)

            if existing_members:
                return Response(
                    {
                        "error": "Some users are already member of company",
                        "company_users": existing_members,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            company_invitations = self._create_invitations(
                emails,
                company.id,
            )

            for invitation in company_invitations:
                async_task(
                    "apps.company.tasks.company_invitation",
                    invitation.email,
                    company.id,
                    invitation.id,
                    request.user.email,
                )

            return Response(
                {"message": "Emails sent successfully"}, status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, company_slug, pk):
        company_member_invite = get_object_or_404(
            CompanyMemberInvite,
            pk=pk,
            company__slug=company_slug,
        )
        company_member_invite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCompanyInvitationsEndpoint(views.APIView):
    model = CompanyMemberInvite

    def get(self, request):
        qs = self.model.objects.filter(
            email=request.user.email,
            is_active=True,
        ).select_related(
            "company",
            "created_by",
        )

        return Response(
            CompanyMemberInviteSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        responses = request.data.get("responses", [])

        for response in responses:
            invitation = CompanyMemberInvite.objects.get(
                id=response.get("id"),
            )

            if invitation.email != request.user.email:
                return Response(
                    {
                        "error": "You do not have permission to respond to this invitation"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if response.get("response") == "accept":
                # Create a new company member
                member = CompanyMember.objects.create(
                    company=invitation.company,
                    member=request.user,
                    role=invitation.role,
                )

                member.permissions.set(invitation.permissions.all())

            invitation.is_active = False
            invitation.accepted = response.get("response") == "accept"
            invitation.responded_at = timezone.now()
            invitation.save()

        return Response(
            {"message": "Companies joined successfully"},
            status=status.HTTP_200_OK,
        )


class UserCompanyJoinEndpoint(views.APIView):
    model = CompanyMemberInvite

    def _decode_token(self, token):
        decoded_token = json.loads(urlsafe_base64_decode(token).decode("utf-8"))
        if not decoded_token:
            return None
        return decoded_token

    def get(self, request):
        token = request.headers.get("X-Invitation-Token")
        if not token:
            return Response(
                {"error": "Invitation token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # decode the token
        decoded_token = self._decode_token(token)

        if not decoded_token:
            return Response(
                {"error": "Invalid invitation token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            invitation = CompanyMemberInvite.objects.get(
                id=decoded_token.get("id"),
                email=decoded_token.get("email"),
                company__slug=decoded_token.get("company_slug"),
                is_active=True,
            )
        except CompanyMemberInvite.DoesNotExist:
            return Response(
                {"error": "Invalid invitation token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CompanyMemberInviteSerializer(invitation).data,
            status=status.HTTP_200_OK,
        )

    @permission_classes([AllowAny])
    def post(self, request):
        token = request.data.get("token")
        accept_or_reject = request.data.get("response")

        if not token:
            return Response(
                {"error": "Invitation token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if accept_or_reject not in ["accept", "reject"]:
            return Response(
                {"error": "Invalid response"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.is_authenticated and accept_or_reject == "accept":
            return Response(
                {"error": "You must be logged in to accept the invitation"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decoded_token = self._decode_token(token)
        if not decoded_token:
            return Response(
                {"error": "Invalid invitation token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            invitation = CompanyMemberInvite.objects.get(
                id=decoded_token.get("id"),
                email=decoded_token.get("email"),
                company__slug=decoded_token.get("company_slug"),
                is_active=True,
            )
        except CompanyMemberInvite.DoesNotExist:
            return Response(
                {"error": "Invalid invitation token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_authenticated:
            if request.user.email != invitation.email:
                return Response(
                    {
                        "error": "You do not have permission to respond to this invitation"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        invitation.accepted = accept_or_reject == "accept"
        invitation.responded_at = timezone.now()
        invitation.is_active = False
        invitation.save()

        if accept_or_reject == "accept":
            # Create a new company member
            member = CompanyMember.objects.create(
                company=invitation.company,
                member=request.user,
                role=invitation.role,
            )

            member.permissions.set(invitation.permissions.all())

        return Response(
            {"message": f"Company invitation {accept_or_reject}ed"},
            status=status.HTTP_200_OK,
        )


class UserCompaniesEndpoint(views.APIView):
    model = Company

    def get(self, request):
        user_companies = Company.objects.filter(
            company_members__member=request.user,
            company_members__is_active=True,
        )

        return Response(
            CompanyLiteSerializer(user_companies, many=True).data,
            status=status.HTTP_200_OK,
        )


class UserCompanySwitchEndpoint(views.APIView):
    model = Company

    def patch(self, request):
        if not request.data.get("company_slug"):
            return Response(
                {"error": "Company slug is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = get_object_or_404(
            Company,
            slug=request.data.get("company_slug"),
            company_members__member=request.user,
            company_members__is_active=True,
        )

        request.user.last_company_id = company.id
        request.user.save()
        return Response(status=status.HTTP_200_OK)
