from allauth.headless.constants import Client
from django.urls import include, re_path

from .views import EmailCheckView, RequestEmailVerificationView, oauth2_callback

urlpatterns = [
    re_path(
        r"^_allauth/app/v1/auth/provider/callback/google",
        oauth2_callback,
        name="google-callback",
    ),
    re_path(
        r"^_allauth/app/v1/auth/email/check$",
        EmailCheckView.as_api_view(client=Client.APP),
        name="email-check",
    ),
    re_path(
        r"^_allauth/browser/v1/auth/email/check$",
        EmailCheckView.as_api_view(client=Client.BROWSER),
        name="email-check",
    ),
    re_path(
        r"^_allauth/app/v1/auth/email/request-verification$",
        RequestEmailVerificationView.as_api_view(client=Client.APP),
        name="request-email-verification",
    ),
    re_path(
        r"^_allauth/browser/v1/auth/email/request-verification$",
        RequestEmailVerificationView.as_api_view(client=Client.BROWSER),
        name="request-email-verification",
    ),
    re_path(r"^_allauth/", include("allauth.headless.urls")),
    re_path(r"^accounts/", include("allauth.urls")),
]
