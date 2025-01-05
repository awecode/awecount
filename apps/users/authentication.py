from rest_framework import authentication, exceptions

from apps.api.models import AccessKey


class AccessKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        secret = request.META.get("HTTP_SECRET")
        if secret:
            user = AccessKey.get_user(secret)
            if not user:
                raise exceptions.AuthenticationFailed("Invalid secret key!")
            return user, None
