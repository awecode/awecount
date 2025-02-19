from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_field
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

    # def populate_username(self, request, user):
    #     user_field(user, app_settings.USER_MODEL_USERNAME_FIELD, user_email(user))


class AllAuthHeadlessAdapter(DefaultHeadlessAdapter):
    def serialize_user(self, user: User):
        ret = super().serialize_user(user)

        ret["avatar"] = (
            user_field(user, "avatar").url if user_field(user, "avatar") else None
        )

        ret["redirect"] = get_redirection_path(user)

        return ret


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
