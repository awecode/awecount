from apps.company.models import Company, CompanyMemberInvite
from apps.users.models import Profile


def get_redirection_path(user):
    # Handle redirections
    profile, _ = Profile.objects.get_or_create(user=user)

    # Redirect to onboarding if the user is not onboarded yet
    if not profile.is_onboarded:
        return "onboarding"

    # Redirect to the last company if the user has last company
    if (
        profile.last_company_id
        and Company.objects.filter(
            pk=profile.last_company_id,
            company_member__member_id=user.id,
            company_member__is_active=True,
        ).exists()
    ):
        company = Company.objects.filter(
            pk=profile.last_company_id,
            company_member__member_id=user.id,
            company_member__is_active=True,
        ).first()
        return f"{company.slug}"

    fallback_company = (
        Company.objects.filter(
            company_member__member_id=user.id, company_member__is_active=True
        )
        .order_by("created_at")
        .first()
    )

    # Redirect to fallback company
    if fallback_company:
        return f"{fallback_company.slug}"

    # Redirect to invitations if the user has unaccepted invitations
    if CompanyMemberInvite.objects.filter(email=user.email).count():
        return "invitations"

    # Redirect the user to create company
    return "create-company"
