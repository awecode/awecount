from django.urls import include, path

from .views import oauth2_callback

urlpatterns = [
    path(
        "_allauth/app/v1/auth/provider/callback/google",
        oauth2_callback,
        name="google-callback",
    ),
    path("_allauth/", include("allauth.headless.urls")),
    path("accounts/", include("allauth.urls")),
]
