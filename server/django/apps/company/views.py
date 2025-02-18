from datetime import datetime

import jwt
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, views, viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.company.models import Company, CompanyMember, CompanyMemberInvite, Permission
from apps.company.permissions import CompanyBasePermission, CompanyAdminPermission, CompanyMemberPermission
from apps.company.serializers import (
    CompanyLiteSerializer,
    CompanyMemberInviteSerializer,
    CompanyMemberSerializer,
    CompanySerializer,
)
from apps.users.models import User


class CompanyInvitationsViewset(viewsets.ModelViewSet):
    """Endpoint for creating, listing and  deleting companys"""

    model = CompanyMemberInvite
    serializer_class = CompanyMemberInviteSerializer

    permission_classes = [CompanyAdminPermission]

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .filter(company__slug=self.kwargs.get("company_slug"))
            .select_related("company", "company__owner", "created_by")
        )


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
            "owner": ["member", "admin"]
        }

        allowed_roles = role_permissions.get(requesting_user.role, [])
        if not allowed_roles:
            raise ValidationError("Members cannot invite anyone")

        for email_data in emails:
            role = email_data.get("role", "member")
            if role not in allowed_roles:
                raise ValidationError(f"{requesting_user.role.title()}s can only invite {' and '.join(allowed_roles)}")

    def _check_existing_members(self, company_id, emails):
        """Check if any invited users are already company members."""
        existing_members = CompanyMember.objects.filter(
            company_id=company_id,
            member__email__in=[email.get("email") for email in emails],
            is_active=True
        ).select_related("member", "company", "company__owner")

        if existing_members.exists():
            return CompanyMemberSerializer(existing_members, many=True).data
        return None

    def _create_invitations(self, emails, company_id, created_by):
        """Create invitation objects for each email."""
        invitations = []
        for email_data in emails:
            email = email_data.get("email").strip().lower()
            token = jwt.encode(
                {
                    "email": email_data,
                    "timestamp": datetime.now().timestamp()
                },
                settings.SECRET_KEY,
                algorithm="HS256"
            )

            invitations.append(
                CompanyMemberInvite(
                    email=email,
                    company_id=company_id,
                    token=token,
                    role=email_data.get("role", "member"),
                    created_by=created_by
                )
            )

        return CompanyMemberInvite.objects.bulk_create(
            invitations,
            batch_size=10,
            ignore_conflicts=True
        )

    def create(self, request, company_slug):
        try:
            emails = request.data.get("emails", [])
            self._validate_emails(emails)

            requesting_user = CompanyMember.objects.get(
                company__slug=company_slug,
                member=request.user,
                is_active=True
            )

            self._validate_permissions(requesting_user, emails)

            company = Company.objects.get(slug=company_slug)
            existing_members = self._check_existing_members(company.id, emails)

            if existing_members:
                return Response(
                    {
                        "error": "Some users are already member of company",
                        "company_users": existing_members
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            company_invitations = self._create_invitations(
                emails,
                company.id,
                request.user
            )

            # Commented out email sending logic as in original
            # current_site = request.META.get("HTTP_ORIGIN")
            # for invitation in company_invitations:
            #     company_invitation.delay(
            #         invitation.email,
            #         company.id,
            #         invitation.token,
            #         current_site,
            #         request.user.email,
            #     )

            return Response(
                {"message": "Emails sent successfully"},
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, company_slug, pk):
        company_member_invite = get_object_or_404(
            CompanyMemberInvite, pk=pk, company__slug=company_slug,
        )
        company_member_invite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyJoinEndpoint(views.APIView):
    permission_classes = [AllowAny]
    """Invitation response endpoint the user can respond to the invitation"""

    def post(self, request, company_slug, pk):
        company_invite = CompanyMemberInvite.objects.get(
            pk=pk, company__slug=company_slug
        )

        email = request.data.get("email", "")

        # Check the email
        if email == "" or company_invite.email != email:
            return Response(
                {"error": "You do not have permission to join the company"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # If already responded then return error
        if company_invite.responded_at is None:
            company_invite.accepted = request.data.get("accepted", False)
            company_invite.responded_at = timezone.now()
            company_invite.save()

            if company_invite.accepted:
                # Check if the user created account after invitation
                user = User.objects.filter(email=email).first()

                # If the user is present then create the company member
                if user is not None:
                    # Check if the user was already a member of company then activate the user
                    company_member = CompanyMember.objects.filter(
                        company=company_invite.company, member=user
                    ).first()
                    if company_member is not None:
                        company_member.is_active = True
                        company_member.role = company_invite.role
                        company_member.save()
                    else:
                        # Create a Company
                        _ = CompanyMember.objects.create(
                            company=company_invite.company,
                            member=user,
                            role=company_invite.role,
                        )

                    # Set the user last_company_id to the accepted company
                    user.last_company_id = company_invite.company.id
                    user.save()

                    # Delete the invitation
                    company_invite.delete()

                # # Send event
                # company_invite_event.delay(
                #     user=user.id if user is not None else None,
                #     email=email,
                #     user_agent=request.META.get("HTTP_USER_AGENT"),
                #     ip=request.META.get("REMOTE_ADDR"),
                #     event_name="MEMBER_ACCEPTED",
                #     accepted_from="EMAIL",
                # )

                return Response(
                    {"message": "Company Invitation Accepted"},
                    status=status.HTTP_200_OK,
                )

            # Company invitation rejected
            return Response(
                {"message": "Company Invitation was not accepted"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "You have already responded to the invitation request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request, company_slug, pk):
        company_invitation = CompanyMemberInvite.objects.get(
            company__slug=company_slug, pk=pk
        )
        serializer = CompanyMemberInviteSerializer(company_invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCompanyInvitationsViewSet(viewsets.ModelViewSet):
    model = CompanyMemberInvite
    serializer_class = CompanyMemberInviteSerializer

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .filter(email=self.request.user.email)
            .select_related("company", "company__owner", "created_by")
            .annotate(total_members=Count("company__company_member"))
        )

    def create(self, request, *args, **kwargs):
        invitations = request.data.get("invitations", [])
        company_invitations = CompanyMemberInvite.objects.filter(
            pk__in=invitations,
            email=request.user.email,
        ).order_by("-created_at")

        # If the user is already a member of company and was deactivated then activate the user
        for invitation in company_invitations:
            CompanyMember.objects.filter(
                company_id=invitation.company_id,
                member=request.user,
            ).update(is_active=True, role=invitation.role)

        # Bulk create the user for all the companys
        CompanyMember.objects.bulk_create(
            [
                CompanyMember(
                    company=invitation.company,
                    member=request.user,
                    role=invitation.role,
                    created_by=request.user,
                )
                for invitation in company_invitations
            ],
            ignore_conflicts=True,
        )

        # Delete joined company invites
        company_invitations.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
        )

        request.user.last_company_id = company.id
        request.user.save()
        return Response(status=status.HTTP_200_OK)


class CompanyMemberViewSet(viewsets.ModelViewSet):
    model = CompanyMember
    serializer_class = CompanyMemberSerializer

    permission_classes = [CompanyAdminPermission]

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .filter(company__slug=self.kwargs.get("company_slug"))
            .select_related("company", "member", "company__owner")
        )

    def destroy(self, request, company_slug, pk):
        company_member = CompanyMember.objects.get(pk=pk, company__slug=company_slug)
        company_member.is_active = False
        company_member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyPermissionEndpoint(views.APIView):
    model = Permission
    permission_classes = [CompanyMemberPermission]

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

class CompanyViewset(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    model = Company
    serializer_class = CompanySerializer
    permission_classes = [CompanyBasePermission]

    lookup_field = "slug"
    lookup_url_kwarg = "company_slug"

    def get_queryset(self):
        return self.model.objects.filter(slug=self.kwargs.get("company_slug"))
