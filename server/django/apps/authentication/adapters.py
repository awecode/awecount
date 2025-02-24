from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field
from allauth.core.internal import httpkit
from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.google.views import (
    GoogleOAuth2Adapter as AllauthGoogleOAuth2Adapter,
)
from django.conf import settings

from apps.authentication.helpers.redirection_path import get_redirection_path
from apps.users.models import User


# class AccountAdapter(EmailAsUsernameAdapter, AllAuthOtpAdapter):
class AllAuthAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return settings.SIGNUP_ALLOWED

    def populate_user(self, request, user):
        user_field(user, "full_name", user_email(user).split("@")[0].title())
        super().populate_user(request, user)


class AllAuthHeadlessAdapter(DefaultHeadlessAdapter):
    def serialize_user(self, user: User):
        ret = super().serialize_user(user)

        return {
            "is_onboarded": getattr(user, "profile", None)
            and getattr(user.profile, "is_onboarded", False),
            "redirect": get_redirection_path(user),
            "full_name": user_field(user, "full_name"),
            "email": ret["email"],
        }


class GoogleOAuth2Adapter(AllauthGoogleOAuth2Adapter):
    def get_callback_url(self, request, app):
        return httpkit.get_frontend_url(
            request,
            "socialaccount_callback",
        ).format(provider="google")


class AllAuthSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_provider(self, request, provider, client_id=None):
        provider_class = super().get_provider(request, provider, client_id)
        if provider == "google":
            provider_class.oauth2_adapter_class = GoogleOAuth2Adapter
        return provider_class
