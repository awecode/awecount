from rest_framework import authentication
from rest_framework import exceptions

from apps.users.models import AccessKey


class AccessKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        secret = request.META.get('HTTP_SECRET')
        user = AccessKey.get_user(secret)
        if not user:
            raise exceptions.AuthenticationFailed('Invalid secret key!')
        return user, None
