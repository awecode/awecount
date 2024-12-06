from django.urls import path

from .views import oauth2_callback

urlpatterns = [
    path(
        "_allauth/app/v1/auth/provider/callback/google",
        oauth2_callback,
        name="google-callback",
    ),
]
