from apps.company.models import CompanyMember, CompanyMemberInvite


def process_company_invitations(user):
    """This function takes in User and adds him to all companies that the user has accepted invited of"""

    # Check if user has any accepted invites for company and add them to company
    company_member_invites = CompanyMemberInvite.objects.filter(
        email=user.email, accepted=True
    )

    CompanyMember.objects.bulk_create(
        [
            CompanyMember(
                company_id=company_member_invite.company_id,
                member=user,
                role=company_member_invite.role,
            )
            for company_member_invite in company_member_invites
        ],
        ignore_conflicts=True,
    )

    # Delete all the invites
    company_member_invites.delete()
