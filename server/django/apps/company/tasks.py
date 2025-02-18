from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.company.models import Company, CompanyMemberInvite


def company_invitation(email, company_id, invitation_id, invitor):
    User = get_user_model()
    user = User.objects.get(email=invitor)

    company = Company.objects.get(pk=company_id)
    company_member_invite = CompanyMemberInvite.objects.get(
        id=invitation_id, email=email
    )

    # Relative link
    relative_link = f"/invitations/{company_member_invite.get_token()}"

    # The complete url including the domain
    abs_url = str(settings.APP_URL) + relative_link

    # Subject of the email
    subject = f"{user.first_name or user.display_name or user.email} has invited you to join them in {company.name} on Awecount"

    context = {
        "email": email,
        "first_name": user.first_name or user.display_name or user.email,
        "company_name": company.name,
        "abs_url": abs_url,
    }

    html_content = render_to_string(
        "emails/invitations/company_invitation.html", context
    )

    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def cleanup_company_invitation(invitation_id):
    company_member_invite = CompanyMemberInvite.objects.get(id=invitation_id)
    company_member_invite.delete()
