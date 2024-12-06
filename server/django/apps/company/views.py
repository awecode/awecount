# Python imports
from datetime import datetime

import jwt

# Django imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count
from django.utils import timezone

# Module imports
from plane.app.permissions import CompanyAdminPermission
from plane.app.serializers import (
    CompanyMemberInviteSerializer,
    CompanyMemberSerializer,
)
from plane.app.views.base import BaseAPIView
from plane.bgtasks.company_invitation_task import company_invitation
from plane.bgtasks.event_tracking_task import company_invite_event
from plane.db.models import Company, CompanyMember, CompanyMemberInvite, User
from plane.utils.cache import invalidate_cache, invalidate_cache_directly

# Third party modules
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .. import BaseViewSet


class CompanyInvitationsViewset(BaseViewSet):
    """Endpoint for creating, listing and  deleting companys"""

    serializer_class = CompanyMemberInviteSerializer
    model = CompanyMemberInvite

    permission_classes = [CompanyAdminPermission]

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .filter(company__slug=self.kwargs.get("slug"))
            .select_related("company", "company__owner", "created_by")
        )

    def create(self, request, slug):
        emails = request.data.get("emails", [])
        # Check if email is provided
        if not emails:
            return Response(
                {"error": "Emails are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # check for role level of the requesting user
        requesting_user = CompanyMember.objects.get(
            company__slug=slug, member=request.user, is_active=True
        )

        # Check if any invited user has an higher role
        if len(
            [
                email
                for email in emails
                if int(email.get("role", 5)) > requesting_user.role
            ]
        ):
            return Response(
                {"error": "You cannot invite a user with higher role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the company object
        company = Company.objects.get(slug=slug)

        # Check if user is already a member of company
        company_members = CompanyMember.objects.filter(
            company_id=company.id,
            member__email__in=[email.get("email") for email in emails],
            is_active=True,
        ).select_related("member", "company", "company__owner")

        if company_members:
            return Response(
                {
                    "error": "Some users are already member of company",
                    "company_users": CompanyMemberSerializer(
                        company_members, many=True
                    ).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        company_invitations = []
        for email in emails:
            try:
                validate_email(email.get("email"))
                company_invitations.append(
                    CompanyMemberInvite(
                        email=email.get("email").strip().lower(),
                        company_id=company.id,
                        token=jwt.encode(
                            {"email": email, "timestamp": datetime.now().timestamp()},
                            settings.SECRET_KEY,
                            algorithm="HS256",
                        ),
                        role=email.get("role", 5),
                        created_by=request.user,
                    )
                )
            except ValidationError:
                return Response(
                    {
                        "error": f"Invalid email - {email} provided a valid email address is required to send the invite"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Create company member invite
        company_invitations = CompanyMemberInvite.objects.bulk_create(
            company_invitations, batch_size=10, ignore_conflicts=True
        )

        current_site = request.META.get("HTTP_ORIGIN")

        # Send invitations
        for invitation in company_invitations:
            company_invitation.delay(
                invitation.email,
                company.id,
                invitation.token,
                current_site,
                request.user.email,
            )

        return Response(
            {"message": "Emails sent successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, request, slug, pk):
        company_member_invite = CompanyMemberInvite.objects.get(
            pk=pk, company__slug=slug
        )
        company_member_invite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanyJoinEndpoint(BaseAPIView):
    permission_classes = [AllowAny]
    """Invitation response endpoint the user can respond to the invitation"""

    @invalidate_cache(path="/api/companys/", user=False)
    @invalidate_cache(path="/api/users/me/companys/", multiple=True)
    @invalidate_cache(
        path="/api/companys/:slug/members/",
        user=False,
        multiple=True,
        url_params=True,
    )
    @invalidate_cache(path="/api/users/me/settings/", multiple=True)
    def post(self, request, slug, pk):
        company_invite = CompanyMemberInvite.objects.get(pk=pk, company__slug=slug)

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

                # Send event
                company_invite_event.delay(
                    user=user.id if user is not None else None,
                    email=email,
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                    ip=request.META.get("REMOTE_ADDR"),
                    event_name="MEMBER_ACCEPTED",
                    accepted_from="EMAIL",
                )

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

    def get(self, request, slug, pk):
        company_invitation = CompanyMemberInvite.objects.get(company__slug=slug, pk=pk)
        serializer = CompanyMemberInviteSerializer(company_invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCompanyInvitationsViewSet(BaseViewSet):
    serializer_class = CompanyMemberInviteSerializer
    model = CompanyMemberInvite

    def get_queryset(self):
        return self.filter_queryset(
            super()
            .get_queryset()
            .filter(email=self.request.user.email)
            .select_related("company", "company__owner", "created_by")
            .annotate(total_members=Count("company__company_member"))
        )

    @invalidate_cache(path="/api/companys/", user=False)
    @invalidate_cache(path="/api/users/me/companys/", multiple=True)
    def create(self, request):
        invitations = request.data.get("invitations", [])
        company_invitations = CompanyMemberInvite.objects.filter(
            pk__in=invitations, email=request.user.email
        ).order_by("-created_at")

        # If the user is already a member of company and was deactivated then activate the user
        for invitation in company_invitations:
            invalidate_cache_directly(
                path=f"/api/companys/{invitation.company.slug}/members/",
                user=False,
                request=request,
                multiple=True,
            )
            # Update the CompanyMember for this specific invitation
            CompanyMember.objects.filter(
                company_id=invitation.company_id, member=request.user
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
