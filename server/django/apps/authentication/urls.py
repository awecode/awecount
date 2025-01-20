from django.urls import include, re_path

from .views import oauth2_callback

urlpatterns = [
    re_path(
        r"^_allauth/app/v1/auth/provider/callback/google",
        oauth2_callback,
        name="google-callback",
    ),
    re_path(r"^_allauth/", include("allauth.headless.urls")),
    re_path(r"^accounts/", include("allauth.urls")),
]
