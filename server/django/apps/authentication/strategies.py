from allauth.headless.tokens.sessions import SessionTokenStrategy
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken


class SessionAndAccessTokenStrategy(SessionTokenStrategy):
    def create_access_token_payload(self, request: HttpRequest) -> dict | None:
        refresh = RefreshToken.for_user(request.user)

        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
